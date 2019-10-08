/*
 * Copyright © 2019 Jerome Flesch
 *
 * Pypillowfight is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, version 2 of the License.
 *
 * Pypillowfight is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, see <http://www.gnu.org/licenses/>.
 */

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <pillowfight/pillowfight.h>
#include <pillowfight/util.h>

#ifndef NO_PYTHON
#include "_pymod.h"
#endif


#define MIN_INTENSITY_A 10
#define MIN_INTENSITY_B 128
#define ANGLE_TOLERANCE ((5 * M_PI) / 180)
#define MIN_SIZE(v) ((v) * 1) / 3
#define MAX_STACK (64 * 1024)

/*!
 * \brief Algorithm to detect page borders on a scanned image.
 *
 * Looks for horizontal and vertical lines.
 */

static void filter_angles(
		struct pf_dbl_matrix *matrix_intensity,
		const struct pf_dbl_matrix *matrix_direction,
		double target_angle
	)
{
	int x, y;
	int intensity;
	double angle, angle_diff;

	assert(matrix_intensity->size.x == matrix_direction->size.x);
	assert(matrix_intensity->size.y == matrix_direction->size.y);

	for (x = 0 ; x < matrix_intensity->size.x ; x++) {
		for (y = 0 ; y < matrix_intensity->size.y ; y++) {

			intensity = PF_MATRIX_GET(matrix_intensity, x, y);

			if (intensity <= MIN_INTENSITY_A) {
				PF_MATRIX_SET(matrix_intensity, x, y, 0);
				continue;
			}

			angle = PF_MATRIX_GET(matrix_direction, x, y);
			angle_diff = (
				fmod(
					(angle - target_angle + (M_PI / 2) + M_PI),
					M_PI
				) - (M_PI / 2)
			);

			if (angle_diff < -1  * ANGLE_TOLERANCE) {
				PF_MATRIX_SET(matrix_intensity, x, y, 0);
				continue;
			}
			if (angle_diff > ANGLE_TOLERANCE) {
				PF_MATRIX_SET(matrix_intensity, x, y, 0);
				continue;
			}

			PF_MATRIX_SET(matrix_intensity, x, y, 255);
		}
	}
}


static void filter_intensities(struct pf_dbl_matrix *matrix_intensity)
{
	int x, y;
	int intensity;

	for (x = 0 ; x < matrix_intensity->size.x ; x++) {
		for (y = 0 ; y < matrix_intensity->size.y ; y++) {

			intensity = PF_MATRIX_GET(matrix_intensity, x, y);

			if (intensity <= MIN_INTENSITY_B) {
				PF_MATRIX_SET(matrix_intensity, x, y, 0);
			} else {
				PF_MATRIX_SET(matrix_intensity, x, y, 255);
			}
		}
	}
}


static struct pf_rectangle find_shape(
		const struct pf_dbl_matrix *intensity_x,
		const struct pf_dbl_matrix *intensity_y
	)
{
	struct pf_rectangle rect = {
		.a = {
			.x = intensity_x->size.x,
			.y = intensity_x->size.y,
		},
		.b = {
			.x = 0,
			.y = 0,
		},
	};

	int x, y, intensity;

	for (x = 0 ; x < intensity_x->size.x ; x++) {
		for (y = 0 ; y < intensity_x->size.y ; y++) {
			intensity = PF_MATRIX_GET(intensity_x, x, y);
			if (intensity != 0) {
				rect.a.x = MIN(rect.a.x, x);
				rect.b.x = MAX(rect.b.x, x);
			}

			intensity = PF_MATRIX_GET(intensity_y, x, y);
			if (intensity != 0) {
				rect.a.y = MIN(rect.a.y, y);
				rect.b.y = MAX(rect.b.y, y);
			}
		}
	}

	return rect;
}


#ifndef NO_PYTHON
static
#endif
struct pf_rectangle pf_find_scan_border(const struct pf_bitmap *img_in)
{
	struct pf_gradient_matrixes gradient;
	struct pf_dbl_matrix x, y, xg, yg;
	struct pf_dbl_matrix in;
	struct pf_rectangle rect;

	in = pf_dbl_matrix_new(img_in->size.x, img_in->size.y);
	pf_rgb_bitmap_to_grayscale_dbl_matrix(img_in, &in);

	gradient = pf_sobel_on_matrix(
		&in,
		PF_SOBEL_DEFAULT_KERNEL_X,
		PF_SOBEL_DEFAULT_KERNEL_Y,
		2.0, 5
	);
	pf_dbl_matrix_free(&in);

	// free intermediate matrix computed by the Sobel operator
	pf_dbl_matrix_free(&gradient.g_x);
	pf_dbl_matrix_free(&gradient.g_y);

	// keep horizontals and verticals only
	x = pf_dbl_matrix_copy(&gradient.intensity);
	y = pf_dbl_matrix_copy(&gradient.intensity);
	pf_dbl_matrix_free(&gradient.intensity);
	filter_angles(&x, &gradient.direction, 0);
	filter_angles(&y, &gradient.direction, M_PI / 2);
	pf_dbl_matrix_free(&gradient.direction);

	xg = pf_gaussian_on_matrix(&x, 1.0, 3);
	yg = pf_gaussian_on_matrix(&y, 1.0, 3);
	pf_dbl_matrix_free(&x);
	pf_dbl_matrix_free(&y);

	filter_intensities(&xg);
	filter_intensities(&yg);

	rect = find_shape(&xg, &yg);
	pf_dbl_matrix_free(&xg);
	pf_dbl_matrix_free(&yg);

	return rect;
}


#ifndef NO_PYTHON
PyObject *pyfind_scan_border(PyObject *self, PyObject* args)
{
	int img_x, img_y;
	Py_buffer img_in;
	struct pf_bitmap bitmap_in;
	struct pf_rectangle frame;

	if (!PyArg_ParseTuple(args, "iiy*",
				&img_x, &img_y,
				&img_in)) {
		return NULL;
	}

	assert(img_x * img_y * 4 /* RGBA */ == img_in.len);

	bitmap_in = from_py_buffer(&img_in, img_x, img_y);

	Py_BEGIN_ALLOW_THREADS;
	frame = pf_find_scan_border(&bitmap_in);
	Py_END_ALLOW_THREADS;

	PyBuffer_Release(&img_in);

	return Py_BuildValue(
		"iiii",
		frame.a.x, frame.a.y,
		frame.b.x, frame.b.y
	);
}

#endif // !NO_PYTHON

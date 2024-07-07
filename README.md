# libpillowfight / pypillowfight

Really simple C Library containing various image processing algorithms.
It includes Python 3 bindings designed to operate on Pillow images (PIL.Image).

The C library depends only on the libc.
The Python bindings depend only on Pillow.

APIs are designed to be as simple to use as possible. Default values are provided
for every parameters.

Python 2.x is *not* supported.

Available algorithms are listed below.

## Available algorithms

* [Unpaper](https://github.com/Flameeyes/unpaper)'s algorithms
  * Blackfilter
  * Noisefilter
  * Blurfilter
  * Masks
  * Grayfilter
  * Border
* Canny edge detection
* Sobel operator
* Gaussian blur
* ACE (Automatic Color Equalization ; Parallelized implementation)
* SWT (Stroke Width Transformation)
* Compare: Compare two images (grayscale) and makes the pixels that are different
  really visible (red).
* Scan borders: Tries to detect the borders of a page in an image coming from
  a scanner.


## Python API

The Python API can be compiled, installed and used without installing the C library.

### Installation

Latest release :

```sh
$ sudo pip3 install pypillowfight
```

Development version :

```sh
$ git clone https://github.com/openpaperwork/libpillowfight.git
$ cd libpillowfight

# Both C library and Python module
$ make
$ sudo make install  # will run python3 ./setup.py install + make install (CMake)

# Or just the Python bindings
$ make build_py
$ make install_py  # will run only python3 ./setup.py install
```

### Usage

For each algorithm, a function is available. It takes a PIL.Image instance as parameter.
It may take other optionnal parameters. The return value is another PIL.Image instance.

Example:

```py
import pillowfight

input_img = PIL.Image.open("tests/data/brightness_problem.png")
output_img = pillowfight.ace(input_img)
```

### Tests

```sh
make check  # will check style
make test  # will run the tests (will require pytest)
```

Test reference images are made on amd64. They should match also on i386.
On other architectures however, due to slight differences regarding floating
point numbers, results may vary slightly and tests may not pass.


## C library

### Installation

```sh
# C library only (will use CMake)
$ make build_c
$ sudo make install_c
```

### Usage

#### C code

For each algorithm, a function is available. It takes a ```struct pf_bitmap```
as input. As output, it fills in another ```struct pf_bitmap```.

```struct pf_bitmap``` is a really simple structure:

```C
struct pf_bitmap {
	struct {
		int x;
		int y;
	} size;
	union pf_pixel *pixels;
};
```

```(struct pf_bitmap).size.x``` is the width of the image.

```(struct pf_bitmap).size.y``` is the height of the image.

```union pf_pixel``` are basically 32 bits integers, defined in a manner convenient
to retrieve each color independantly (RGB). Each color is on one byte. 4th byte is
unused (no alpha channel taken into account).

```(struct pf_bitmap).pixels``` must points to a memory area containing the image.
The image must contains ```x * y * union pf_pixel```.


#### Compilation with GCC

```
$ gcc -Wall -Werror -lpillowfight -o test test.c
```


## Note regarding Unpaper's algorithms

Many algorithms in this library are re-implementations of algorithms used
by [Unpaper](https://github.com/Flameeyes/unpaper). To make the API simpler
to use (.. and implement), a lot of settings have been hard-coded.

Unpaper applies them in the following order:

* Blackfilter
* Noisefilter
* Blurfilter
* Masks
* Grayfilter
* Border

I would advise applying automatic color equalization (ACE) first.

A basic documentation for some of the algorithms can be found in
[Unpaper's documentation](https://github.com/Flameeyes/unpaper/blob/master/doc/basic-concepts.md).

| Input | Output |
| ----- | ------ |
| [Black border problem](tests/data/black_border_problem.png) | [ACE + Unpapered](tests/data/black_border_problem_all.png) |
| [Brightness problem](tests/data/brightness_problem.png) | [ACE + Unpapered](tests/data/brightness_problem_all.png) |

## Available algorithms

### Automatic Color Equalization (ACE)

| Input | Output |
| ----- | ------ |
| [Brightness problem](tests/data/brightness_problem.png) | [Corrected](tests/data/brightness_problem_ace.png) |

This algorithm is quite slow (~40s for one big image with one thread
on my machine). So this version is parallelized (down to ~15s on a 4
cores computer).


#### Python API

```py
out_img = pillowfight.ace(img_in,
	slope=10,
	limit=1000,
	samples=100,
	seed=None)
```

Use as many threads as there are cores on the computer (up to 32).

This algorithm uses random number. If you need consistent results
(for unit tests for instance), you can specify a seed for the
random number generator. Otherwise, time.time() will be used.


#### C API

```C
#define PF_DEFAULT_ACE_SLOPE 10
#define PF_DEFAULT_ACE_LIMIT 1000
#define PF_DEFAULT_ACE_NB_SAMPLES 100
#define PF_DEFAULT_ACE_NB_THREADS 2
extern void pf_ace(const struct pf_bitmap *in, struct pf_bitmap *out,
		int nb_samples, double slope, double limit,
		int nb_threads);
```

This function uses random numbers coming (```rand()```).
You *should* call ```srand()``` before calling this function.


#### Sources

* "A new algorithm for unsupervised global and local color correction." - A. Rizzi, C. Gatta and D. Marini
* http://argmax.jp/index.php?colorcorrect


### Scan border

This algorithm tries to find page borders in a scanned image. It is designed
to operate on images coming from a flatbed scanner or a scanner with an
automatic document feeder.

This algorithms looks for horizontal and vertical lines, and return the
smallest rectangle that includes all those lines. To get the lines, it runs
the Sobel operator on the input image and only keep the points with
an angle of [0°, 90°, 180°, 270°] ±5°.

This algorithm does not always work:
- It's quite sensible to noise: dust, hair, etc may easily be counted
  erroneously as lines.
- Some scanners or drivers (most of Brother scanners for instance) "clean up"
  the image before returning it. Unfortunately they often remove most of the
  page borders in the process.

Still, this algorithm can help users of GUI applications by pre-selecting a
cropping area.


| Input | Output |
| ----- | ------ |
| [brother_mfc7360n](tests/data/brother_mfc7360.png) | (56, 8, 1637, 2275) |
| [epson_xp425](tests/data/epson_xp425.png) | (4, 5, 2484, 3498) |
| [brother_ds620](tests/data/brother_ds620.png) | (3, 3, 2507, 3527) |

#### Python API

```py
frame = pillowfight.find_scan_borders(img_in)
```


#### C API

```C
struct pf_point {
	int x;
	int y;
};

struct pf_rectangle {
	struct pf_point a;
	struct pf_point b;
};

struct pf_rectangle pf_find_scan_borders(const struct pf_bitmap *img_in);
```


### Canny's edge detection

| Input | Output |
| ----- | ------ |
| [Crappy background](tests/data/crappy_background.png) | [Canny output](tests/data/crappy_background_canny.png) |


#### Python API

```py
img_out = pillowfight.canny(img_in)
```


#### C API

```C
extern void pf_canny(const struct pf_bitmap *in, struct pf_bitmap *out);
```


#### Sources

* "A computational Approach to Edge Detection" - John Canny
* https://en.wikipedia.org/wiki/Canny_edge_detector


### Compare

Simple algorithm showing the difference between two images.
Note that it converts the images to grayscale first.

It accepts a parameter 'tolerance': For each pixel, the difference with
the corresponding pixel from the other image is computed. If the
difference is between 0 and 'tolerance', it is ignored (pixels
are considered equal).

| Input | Input2 | Output |
| ----- | ------ | ------ |
| [Black border problem](tests/data/black_border_problem.png) | [Black border problem + blackfilter](tests/data/black_border_problem_blackfilter.png) | [Diff](tests/data/black_border_problem_diff.png) |

#### Python API

```py
(nb_diff, out_img) = pillowfight.compare(img_in, img_in2, tolerance=10)
```


#### C API

```C
extern int pf_compare(const struct pf_bitmap *in, const struct pf_bitmap *in2,
		struct pf_bitmap *out, int tolerance);
```

Returns the number of pixels that are different between both images.


### Gaussian

| Input | Output |
| ----- | ------ |
| [Crappy background](tests/data/crappy_background.png) | [Gaussed](tests/data/crappy_background_gaussian.png) |

One of the parameters is ```sigma```. If it is equals to 0.0, it will be computed automatically
using the following formula (same as OpenCV):

```C
sigma = 0.3 * ((nb_stddev - 1) * 0.5 - 1) + 0.8;
```

#### Python API

```py
img_out = pillowfight.gaussian(img_in, sigma=2.0, nb_stddev=5)
```


#### C API

```
extern void pf_gaussian(const struct pf_bitmap *in, struct pf_bitmap *out,
	double sigma, int nb_stddev);
```


#### Sources

* https://en.wikipedia.org/wiki/Gaussian_blur
* https://en.wikipedia.org/wiki/Gaussian_function


### Sobel operator

| Input | Output |
| ----- | ------ |
| [Crappy background](tests/data/crappy_background.png) | [Sobel](tests/data/crappy_background_sobel.png) |


#### Python API

```py
img_out = pillowfight.sobel(img_in)
```


#### C API

```C
extern void pf_sobel(const struct pf_bitmap *in_img, struct pf_bitmap *out_img);
```


#### Sources

* https://www.researchgate.net/publication/239398674_An_Isotropic_3_3_Image_Gradient_Operator
* https://en.wikipedia.org/wiki/Sobel_operator


### Stroke Width Transformation

This algorithm extracts text from natural scenes images.

To find text, it looks for strokes. Note that it doesn't appear to work well on
scanned documents because strokes are too small.

This implementation can provide the output in 3 different ways:

* Black & White : Detected text is black. Background is white.
* Grayscale : Detected text is gray. Its exact color is proportional to the stroke width detected.
* Original boxes : The rectangle around the detected is copied as is in the output image. Rest of the image is white.

(following examples are with original boxes)

| Input | Output |
| ----- | ------ |
| [Black border problen](tests/data/black_border_problem.png) | [SWT (SWT_OUTPUT_ORIGINAL_BOXES)](tests/data/black_border_problem_swt.png) |
| [Crappy background](tests/data/crappy_background.png) | [SWT (SWT_OUTPUT_ORIGINAL_BOXES)](tests/data/crappy_background_swt.png) |
| [Black border problen](tests/data/black_border_problem.png) | [SWT (SWT_OUTPUT_BW_TEXT)](tests/data/black_border_problem_swt.png) |
| [Crappy background](tests/data/crappy_background.png) | [SWT (SWT_OUTPUT_BW_TEXT)](tests/data/crappy_background_swt.png) |


#### Python API

```py
# SWT_OUTPUT_BW_TEXT = 0  # default
# SWT_OUTPUT_GRAYSCALE_TEXT = 1
# SWT_OUTPUT_ORIGINAL_BOXES = 2

img_out = pillowfight.swt(img_in, output_type=pillowfight.SWT_OUTPUT_ORIGINAL_BOXES)
```


#### C API

```C
enum pf_swt_output
{
	PF_SWT_OUTPUT_BW_TEXT = 0,
	PF_SWT_OUTPUT_GRAYSCALE_TEXT,
	PF_SWT_OUTPUT_ORIGINAL_BOXES,
};
#define PF_DEFAULT_SWT_OUTPUT PF_SWT_OUTPUT_BW_TEXT

extern void pf_swt(const struct pf_bitmap *in_img, struct pf_bitmap *out_img,
		enum pf_swt_output output_type);
```


#### Sources

* ["Detecting Text in Natural Scenes with Stroke Width Transform"](http://cmp.felk.cvut.cz/~cernyad2/TextCaptchaPdf/Detecting%20Text%20in%20Natural%20Scenes%20with%20Stroke%20Width%20Transform.pdf) - Boris Epshtein, Eyal Ofek, Yonatan Wexler
* https://github.com/aperrau/DetectText


### Unpaper's Blackfilter

| Input | Output | Diff |
| ----- | ------ | ---- |
| [Black border problem](tests/data/black_border_problem.png) | [Filtered](tests/data/black_border_problem_blackfilter.png) | [Diff](tests/data/black_border_problem_blackfilter_diff.png) |


#### Python API

```py
img_out = pillowfight.unpaper_blackfilter(img_in)
```


#### C API

```C
extern void pf_unpaper_blackfilter(const struct pf_bitmap *in, struct pf_bitmap *out);
```


#### Sources

* https://github.com/Flameeyes/unpaper
* https://github.com/Flameeyes/unpaper/blob/master/doc/basic-concepts.md


### Unpaper's Blurfilter

| Input | Output | Diff |
| ----- | ------ | ---- |
| [Black border problem](tests/data/black_border_problem.png) | [Filtered](tests/data/black_border_problem_blurfilter.png) | [Diff](tests/data/black_border_problem_blurfilter_diff.png) |


#### Python API

```py
img_out = pillowfight.unpaper_blurfilter(img_in)
```


#### C API

```C
extern void pf_unpaper_blurfilter(const struct pf_bitmap *in, struct pf_bitmap *out);
```


#### Sources

* https://github.com/Flameeyes/unpaper
* https://github.com/Flameeyes/unpaper/blob/master/doc/basic-concepts.md


### Unpaper's Border

| Input | Output | Diff |
| ----- | ------ | ---- |
| [Black border problem 3](tests/data/black_border_problem3.png) | [Border](tests/data/black_border_problem3_border.png) | [Diff](tests/data/black_border_problem3_border_diff.png) |


#### Python API

```py
img_out = pillowfight.unpaper_border(img_in)
```


#### C API

```C
extern void pf_unpaper_border(const struct pf_bitmap *in, struct pf_bitmap *out);
```


#### Sources

* https://github.com/Flameeyes/unpaper
* https://github.com/Flameeyes/unpaper/blob/master/doc/basic-concepts.md


### Unpaper's Grayfilter

| Input | Output | Diff |
| ----- | ------ | ---- |
| [Black border problem 3](tests/data/black_border_problem.png) | [Filterd](tests/data/black_border_problem_grayfilter.png) | [Diff](tests/data/black_border_problem_grayfilter_diff.png) |


#### Python API

```py
img_out = pillowfight.unpaper_grayfilter(img_in)
```


#### C API

```C
extern void pf_unpaper_grayfilter(const struct pf_bitmap *in, struct pf_bitmap *out);
```


#### Sources

* https://github.com/Flameeyes/unpaper
* https://github.com/Flameeyes/unpaper/blob/master/doc/basic-concepts.md


### Unpaper's Masks

| Input | Output | Diff |
| ----- | ------ | ---- |
| [Black border problem 2](tests/data/black_border_problem2.png) | [Masks](tests/data/black_border_problem2_masks.png) | [Diff](tests/data/black_border_problem2_masks_diff.png) |


#### Python API

```py
img_out = pillowfight.unpaper_masks(img_in)
```


#### C API

```C
extern void pf_unpaper_masks(const struct pf_bitmap *in, struct pf_bitmap *out);
```


#### Sources

* https://github.com/Flameeyes/unpaper
* https://github.com/Flameeyes/unpaper/blob/master/doc/basic-concepts.md


### Unpaper's Noisefilter

| Input | Output | Diff |
| ----- | ------ | ---- |
| [Black border problem](tests/data/black_border_problem.png) | [Filtered](tests/data/black_border_problem_noisefilter.png) | [Diff](tests/data/black_border_problem_noisefilter_diff.png) |


#### Python API

```py
img_out = pillowfight.unpaper_noisefilter(img_in)
```


#### C API

```C
extern void pf_unpaper_noisefilter(const struct pf_bitmap *in, struct pf_bitmap *out);
```


## Contact

* [Forum](https://forum.openpaper.work/)
* [Bug tracker](https://github.com/openpaperwork/libpillowfight/issues/)


#### Sources

* https://github.com/Flameeyes/unpaper
* https://github.com/Flameeyes/unpaper/blob/master/doc/basic-concepts.md

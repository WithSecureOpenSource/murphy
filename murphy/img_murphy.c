#include <stdio.h>
#include <stdint.h>

#define BYTE uint8_t
#define DWORD uint32_t

#ifdef _WIN64
	#define EXPORT __declspec(dllexport)
	#define CALL_TYPE __stdcall
#elif _WIN32
	#define EXPORT __declspec(dllexport)
	#define CALL_TYPE __stdcall
#elif linux
	#define EXPORT
	#define CALL_TYPE
#endif

#ifdef __cplusplus
extern "C" {  // only need to export C interface if
             // used by C++ source code
#endif

// On linux use:
// gcc -c -Werror -fpic img_murphy.c
// gcc -shared -o img_murphy.so img_murphy.o
// On windows, create a solution

//hint: h_x1, h_y1, h_x2, h_y2
EXPORT int CALL_TYPE find(BYTE* search_for, int for_width, int for_height, BYTE* search_in, int in_width, int in_height, int *best_x, int *best_y, BYTE* mask)
{
	int x0, y0, x1, y1;

	int in_ptr, for_ptr;

	int right_gap, right_limit;
	int bottom_limit;
	int matches, mismatches, best_match;
	int diff, half_for_height;

	int xx, yy;
	BYTE mask_val;

	right_limit = in_width - for_width;
	right_gap = right_limit;
	bottom_limit = in_height - for_height;
	half_for_height = 2;

	in_ptr = 0;
	for_ptr = 0;
	best_match = -1;

	xx = *best_x;
	yy = *best_y;
	if( xx < 0 ) {
		xx = -xx;
		right_limit = xx + 1;
	}
	if( yy < 0 ) {
		yy = -yy;
		bottom_limit = yy + 1;
	}
	//printf("Search starts at %i %i ends at %i %i with mask %i\n", xx, yy, right_limit, bottom_limit, mask);

	for( y0 = yy; y0 <= bottom_limit; y0++ ) {
		for( x0 = xx; x0 <= right_limit; x0++ ) {
			in_ptr = (y0 * in_width) + x0;
			for_ptr = 0;
			matches = 0;
			mismatches = 0;
			for( y1 = 0; y1 < for_height; y1++ ) {
				for( x1 = 0; x1 < for_width; x1++ ) {
					if( mask == NULL) {
						diff = (search_in[in_ptr++] - search_for[for_ptr++]) & 0xfff;
					} else {
						mask_val = mask[for_ptr];
						if(mask_val == 0) {
							diff = (search_in[in_ptr++] - search_for[for_ptr++]) & 0xfff;
						} else {
							in_ptr++;
							for_ptr++;
							diff = 0;
						}
					}
					if( diff < 2 ) {
						matches++;
					} else {
						mismatches++;
						if( mismatches > matches && y1 > half_for_height )
							break;
					}
				}
				if( mismatches > matches && y1 > half_for_height )
					break;
				in_ptr += right_gap;
			}

			if( matches > best_match ) {
				best_match = matches;
				*best_x = x0;
				*best_y = y0;
			}
		}
	}

	return best_match;

}

#ifdef __cplusplus
}
#endif

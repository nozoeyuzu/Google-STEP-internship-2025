#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>

#define NUM_BINS 8

// 要求サイズ size → どのビンに入れるか
static int size_to_bin(size_t size) {
    int bin = 0;
    size_t limit = 8;
    while (bin + 1 < NUM_BINS && size > limit) {
        limit <<= 1;  // 8bitごとに
        bin++;
    }
    return bin;
}

typedef struct my_metadata_t {
    size_t size;
    struct my_metadata_t *next;
} my_metadata_t;

// ビンごとの先頭ポインタを持つヒープ管理
typedef struct {
    my_metadata_t *bins[NUM_BINS];
} my_heap_t;

static my_heap_t my_heap;

// 初期化
void my_initialize() {
    for (int i = 0; i < NUM_BINS; i++) {
        my_heap.bins[i] = NULL;
    }
}

// free：メタデータを取り出して対応ビンへプッシュ
void my_free(void *ptr) {
    if (!ptr) return;
    my_metadata_t *m = (my_metadata_t*)ptr - 1;
    int bin = size_to_bin(m->size);
    m->next = my_heap.bins[bin];
    my_heap.bins[bin] = m;
}

// malloc：自分のビン→上位ビンへ順に探し、First‐fit で切り出し
void *my_malloc(size_t size) {
    int start_bin = size_to_bin(size);

    for (int bin = start_bin; bin < NUM_BINS; bin++) {
        my_metadata_t *m = my_heap.bins[bin];
        my_metadata_t *prev = NULL;
        while (m) {
            if (m->size >= size) {
                // リストから取り除き
                if (prev) prev->next = m->next;
                else      my_heap.bins[bin] = m->next;
                m->next = NULL;

                // 分割可能なら余りを新チャンクに
                size_t rem = m->size - size;
                if (rem > sizeof(my_metadata_t)) {
                    m->size = size;
                    my_metadata_t *r = 
                        (my_metadata_t*)(((char*)(m+1)) + size);
                    r->size = rem - sizeof(my_metadata_t);
                    int rbin = size_to_bin(r->size);
                    r->next = my_heap.bins[rbin];
                    my_heap.bins[rbin] = r;
                }
                return (void*)(m + 1);
            }
            prev = m;
            m = m->next;
        }
    }

    // どのビンにもなければシステムからページ単位で確保→最大ビンに追加→再帰
    size_t buf = 4096;
    my_metadata_t *newm = mmap_from_system(buf);
    newm->size = buf - sizeof(my_metadata_t);
    newm->next = my_heap.bins[NUM_BINS - 1];
    my_heap.bins[NUM_BINS - 1] = newm;

    return my_malloc(size);
}
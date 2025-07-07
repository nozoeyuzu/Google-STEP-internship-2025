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
        limit <<= 1;  // 8→16→32→…
        bin++;
    }
    return bin;
}

typedef struct simple_metadata_t {
    size_t size;
    struct simple_metadata_t *next;
} simple_metadata_t;

// ビンごとの先頭ポインタを持つヒープ管理
typedef struct {
    simple_metadata_t *bins[NUM_BINS];
} simple_heap_t;

static simple_heap_t simple_heap;

// システムからページを取ってくるラッパー
void *mmap_from_system(size_t size) {
    void *p = mmap(NULL, size,
                   PROT_READ | PROT_WRITE,
                   MAP_ANONYMOUS | MAP_PRIVATE,
                   -1, 0);
    if (p == MAP_FAILED) {
        perror("mmap");
        exit(1);
    }
    return p;
}
void munmap_to_system(void *ptr, size_t size) {
    munmap(ptr, size);
}

// 初期化：全ビンを空に
void simple_initialize() {
    for (int i = 0; i < NUM_BINS; i++) {
        simple_heap.bins[i] = NULL;
    }
}

// free：メタデータを取り出して対応ビンへプッシュ
void simple_free(void *ptr) {
    if (!ptr) return;
    simple_metadata_t *m = (simple_metadata_t*)ptr - 1;
    int bin = size_to_bin(m->size);
    m->next = simple_heap.bins[bin];
    simple_heap.bins[bin] = m;
}

// malloc：自分のビン→上位ビンへ順に探し、First‐fit で切り出し
void *simple_malloc(size_t size) {
    // 要求は 8 バイト以上、8 の倍数で来る想定
    int start_bin = size_to_bin(size);

    for (int bin = start_bin; bin < NUM_BINS; bin++) {
        simple_metadata_t *m = simple_heap.bins[bin];
        simple_metadata_t *prev = NULL;
        while (m) {
            if (m->size >= size) {
                // リストから取り除き
                if (prev) prev->next = m->next;
                else      simple_heap.bins[bin] = m->next;
                m->next = NULL;

                // 分割可能なら余りを新チャンクに
                size_t rem = m->size - size;
                if (rem > sizeof(simple_metadata_t)) {
                    m->size = size;
                    simple_metadata_t *r = 
                        (simple_metadata_t*)(((char*)(m+1)) + size);
                    r->size = rem - sizeof(simple_metadata_t);
                    int rbin = size_to_bin(r->size);
                    r->next = simple_heap.bins[rbin];
                    simple_heap.bins[rbin] = r;
                }
                return (void*)(m + 1);
            }
            prev = m;
            m = m->next;
        }
    }

    // どのビンにもなければシステムからページ単位で確保→最大ビンに追加→再帰
    size_t buf = 4096;
    simple_metadata_t *newm = mmap_from_system(buf);
    newm->size = buf - sizeof(simple_metadata_t);
    newm->next = simple_heap.bins[NUM_BINS - 1];
    simple_heap.bins[NUM_BINS - 1] = newm;

    return simple_malloc(size);
}
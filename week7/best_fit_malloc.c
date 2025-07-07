#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/time.h>

void *mmap_from_system(size_t size);
void munmap_to_system(void *ptr, size_t size);

// Each object or free slot has metadata just prior to it:
//
// ... | m | object | m | free slot | m | free slot | m | object | ...
//
// where |m| indicates metadata. The metadata is needed for two purposes:
//
// 1) For an allocated object:
//   *  |size| indicates the size of the object. |size| does not include
//      the size of the metadata.
//   *  |next| is unused and set to NULL.
// 2) For a free slot:
//   *  |size| indicates the size of the free slot. |size| does not include
//      the size of the metadata.
//   *  The free slots are linked with a singly linked list (we call this a
//      free list). |next| points to the next free slot.
typedef struct simple_metadata_t {
  size_t size;
  struct simple_metadata_t *next;
} simple_metadata_t;

// The global information of the simple malloc.
//   *  |free_head| points to the first free slot.
//   *  |dummy| is a dummy free slot (only used to make the free list
//      implementation simpler).
typedef struct simple_heap_t {
  simple_metadata_t *free_head;
  simple_metadata_t dummy;
} simple_heap_t;

simple_heap_t simple_heap;

// Add a free slot to the beginning of the free list.
void simple_add_to_free_list(simple_metadata_t *metadata) {
  assert(!metadata->next);
  metadata->next = simple_heap.free_head;
  simple_heap.free_head = metadata;
}

// Remove a free slot from the free list.
void simple_remove_from_free_list(simple_metadata_t *metadata,
                                  simple_metadata_t *prev) {
  if (prev) {
    prev->next = metadata->next;
  } else {
    simple_heap.free_head = metadata->next;
  }
  metadata->next = NULL;
}

// This is called at the beginning of each challenge.
void simple_initialize() {
  simple_heap.free_head = &simple_heap.dummy;
  simple_heap.dummy.size = 0;
  simple_heap.dummy.next = NULL;
}

void *simple_malloc(size_t size) {
  simple_metadata_t *meta = simple_heap.free_head;
  simple_metadata_t *prev = NULL;

  // --- Best-fit 用の変数を用意 ---
  simple_metadata_t *best_meta = NULL;
  simple_metadata_t *best_prev = NULL;
  size_t best_remainder = SIZE_MAX;

  // 空きリスト全体をスキャン
  while (meta) {
    if (meta->size >= size) {
      size_t rem = meta->size - size;
      if (rem < best_remainder) {
        best_remainder = rem;
        best_meta = meta;
        best_prev = prev;
        // 余り 0 ならこれ以上探しても小さくならない → 探索終了もアリ
        if (rem == 0) break;
      }
    }
    prev = meta;
    meta = meta->next;
  }

  // ベストが見つからなかったら mmap してリトライ
  if (!best_meta) {
    size_t buffer_size = 4096;
    simple_metadata_t *new_meta =
      (simple_metadata_t*)mmap_from_system(buffer_size);
    new_meta->size = buffer_size - sizeof(simple_metadata_t);
    new_meta->next = NULL;
    simple_add_to_free_list(new_meta);
    return simple_malloc(size);
  }

  // best_meta／best_prev を使って切り出し
  void *ptr = best_meta + 1;
  size_t remaining_size = best_meta->size - size;
  simple_remove_from_free_list(best_meta, best_prev);

  if (remaining_size > sizeof(simple_metadata_t)) {
    best_meta->size = size;
    simple_metadata_t *new_meta =
      (simple_metadata_t*)((char*)ptr + size);
    new_meta->size = remaining_size - sizeof(simple_metadata_t);
    new_meta->next = NULL;
    simple_add_to_free_list(new_meta);
  }
  return ptr;
}

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
typedef struct my_metadata_t {
  size_t size;
  struct my_metadata_t *next;
} my_metadata_t;

// The global information of the my malloc.
//   *  |free_head| points to the first free slot.
//   *  |dummy| is a dummy free slot (only used to make the free list
//      implementation myr).
typedef struct my_heap_t {
  my_metadata_t *free_head;
  my_metadata_t dummy;
} my_heap_t;

my_heap_t my_heap;

// Add a free slot to the beginning of the free list.
void my_add_to_free_list(my_metadata_t *metadata) {
  assert(!metadata->next);
  metadata->next = my_heap.free_head;
  my_heap.free_head = metadata;
}

// Remove a free slot from the free list.
void my_remove_from_free_list(my_metadata_t *metadata,
                                  my_metadata_t *prev) {
  if (prev) {
    prev->next = metadata->next;
  } else {
    my_heap.free_head = metadata->next;
  }
  metadata->next = NULL;
}

// This is called at the beginning of each challenge.
void my_initialize() {
  my_heap.free_head = &my_heap.dummy;
  my_heap.dummy.size = 0;
  my_heap.dummy.next = NULL;
}

void *my_malloc(size_t size) {
  my_metadata_t *meta = my_heap.free_head;
  my_metadata_t *prev = NULL;

  // --- Best-fit 用の変数を用意 ---
  my_metadata_t *best_meta = NULL;
  my_metadata_t *best_prev = NULL;
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
    my_metadata_t *new_meta =
      (my_metadata_t*)mmap_from_system(buffer_size);
    new_meta->size = buffer_size - sizeof(my_metadata_t);
    new_meta->next = NULL;
    my_add_to_free_list(new_meta);
    return my_malloc(size);
  }

  // best_meta／best_prev を使って切り出し
  void *ptr = best_meta + 1;
  size_t remaining_size = best_meta->size - size;
  my_remove_from_free_list(best_meta, best_prev);

  if (remaining_size > sizeof(my_metadata_t)) {
    best_meta->size = size;
    my_metadata_t *new_meta =
      (my_metadata_t*)((char*)ptr + size);
    new_meta->size = remaining_size - sizeof(my_metadata_t);
    new_meta->next = NULL;
    my_add_to_free_list(new_meta);
  }
  return ptr;
}

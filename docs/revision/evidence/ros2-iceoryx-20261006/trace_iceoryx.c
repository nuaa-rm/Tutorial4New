// 独立低频诊断：拦截真实共享块发布/接收，性能测量不加载此库。
#define _GNU_SOURCE
#include <dlfcn.h>
#include <inttypes.h>
#include <stdatomic.h>
#include <stdio.h>
#include <unistd.h>
#include "dds/ddsi/ddsi_shm_transport.h"

static void record(const char *event, const void *payload) {
  typedef iceoryx_header_t *(*header_fn)(const void *);
  header_fn header_from_chunk = (header_fn)dlsym(dlopen("libddsc.so", RTLD_LAZY | RTLD_NOLOAD), "iceoryx_header_from_chunk");
  const iceoryx_header_t *header = header_from_chunk(payload);
  if (header->data_size < 4000000) return;
  uint64_t hash = UINT64_C(14695981039346656037);
  const unsigned char *bytes = payload;
  for (uint32_t i = 0; i < header->data_size; ++i) {
    hash ^= bytes[i]; hash *= UINT64_C(1099511628211);
  }
  uintptr_t address = (uintptr_t)payload;
  unsigned long start, end, offset, inode;
  char line[512], device[32], object[256] = "";
  FILE *maps = fopen("/proc/self/maps", "r");
  while (fgets(line, sizeof(line), maps)) {
    if (sscanf(line, "%lx-%lx %*s %lx %31s %lu %255s", &start, &end,
               &offset, device, &inode, object) >= 5 && start <= address && address < end) {
      printf("IOX_TRACE {\"event\":\"%s\",\"pid\":%d,\"state\":%d,\"bytes\":%u,"
             "\"hash\":\"%016" PRIx64 "\",\"device\":\"%s\",\"inode\":%lu,"
             "\"object\":\"%s\",\"offset\":%lu}\n", event, getpid(),
             header->shm_data_state, header->data_size, hash,
             device, inode, object, offset + address - start);
      fflush(stdout); break;
    }
  }
  fclose(maps);
}

void iox_pub_publish_chunk(iox_pub_t self, void *payload) {
  typedef void (*publish_fn)(iox_pub_t, void *);
  publish_fn original = (publish_fn)dlsym(dlopen("libiceoryx_binding_c.so", RTLD_LAZY | RTLD_NOLOAD), "iox_pub_publish_chunk");
  record("publish", payload);
  original(self, payload);
}

enum iox_ChunkReceiveResult iox_sub_take_chunk(iox_sub_t self, const void **payload) {
  typedef enum iox_ChunkReceiveResult (*take_fn)(iox_sub_t, const void **);
  take_fn original = (take_fn)dlsym(dlopen("libiceoryx_binding_c.so", RTLD_LAZY | RTLD_NOLOAD), "iox_sub_take_chunk");
  enum iox_ChunkReceiveResult result = original(self, payload);
  if (result == ChunkReceiveResult_SUCCESS) record("take", *payload);
  return result;
}

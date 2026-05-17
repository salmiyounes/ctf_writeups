#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

uint32_t read_seed(unsigned char *data) { return *((uint32_t *)data); }

void decrypt(unsigned char *data, size_t size) {
  unsigned char *ptr = (unsigned char *)(data + sizeof(uint32_t));
  size_t payload_len = (size - sizeof(uint32_t)) / sizeof(uint8_t);

  // Seed random values
  srand(read_seed(data));

  for (size_t i = 0; i < payload_len; i++) {
    int k = rand() & 0xFF;
    int rotation = rand() & 7;

    unsigned char byte = ptr[i];

    if (rotation != 0) {
      byte = (byte >> rotation) | (byte << (8 - rotation));
    }

    byte ^= k;

    putc(byte, stdout);
  }

  putc('\n', stdout);
}

int load_file_content_and_decrypt_flag(const char *file_name) {
  int fd;
  unsigned char *data;
  struct stat sb;
  if ((fd = open(file_name, O_RDONLY)) < 0)
    return -1;

  if (fstat(fd, &sb) < 0)
    return -1;

  if ((data = mmap(NULL, sb.st_size, PROT_READ, MAP_SHARED, fd, 0)) ==
      MAP_FAILED)
    return -1;

  decrypt(data, sb.st_size);

  munmap(data, sb.st_size);
  close(fd);
  return 0;
}

int main(int argc, char **argv) {
  if (argc < 2) {
    fprintf(stderr, "Usage: ./decrypt {file}\n");
    return 1;
  }

  if (load_file_content_and_decrypt_flag(argv[1]) == -1) {
    fprintf(stderr, "Error: Failed to open or process file '%s'\n", argv[1]);
    return 1;
  }

  return 0;
}
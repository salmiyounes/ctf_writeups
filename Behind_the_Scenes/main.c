#define __USE_GNU
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ucontext.h>


void handler(int signo, siginfo_t *sinfo, void *context) {
    ucontext_t *uc = (ucontext_t *) context;
    
    uc->uc_mcontext.gregs[16] += 2; // REG_RIP 
}

int main(int argc, char **argv) {
    struct sigaction sa;
	memset(&sa, 0, sizeof(struct sigaction));
	sigemptyset(&sa.sa_mask);
	sa.sa_flags = SA_SIGINFO;
	sa.sa_sigaction = handler;
	sigaction(SIGILL, &sa, NULL);

	printf("%s", "Reachable\n");

	asm("ud2"); 

	printf("%s", "Unreachable\n");
}
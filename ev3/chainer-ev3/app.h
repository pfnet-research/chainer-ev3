#include "target_test.h"
#define MAIN_PRIORITY	5
#define HIGH_PRIORITY	9
#define MID_PRIORITY	10
#define LOW_PRIORITY	11

#ifndef STACK_SIZE
#define	STACK_SIZE      4096
#endif /* STACK_SIZE */

#ifndef LOOP_REF
#define LOOP_REF        ULONG_C(1000000)
#endif /* LOOP_REF */

#ifndef TOPPERS_MACRO_ONLY

extern void	task(intptr_t exinf);
extern void	main_task(intptr_t exinf);
extern ulong_t  get_time();
extern void     watchdog_task(intptr_t exinf);

#endif /* TOPPERS_MACRO_ONLY */

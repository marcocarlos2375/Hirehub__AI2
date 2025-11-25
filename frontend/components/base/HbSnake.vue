<template>
  <div class="hb-snake" :class="`hb-snake--${size}`">
    <div class="snake"></div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict

interface Props {
  size?: 'xxxs' | 'xxs' | 'xs' | 'sm' | 'md' | 'lg' | 'xl'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})
</script>

<style scoped lang="scss">
.hb-snake {
  display: inline-block;
  position: relative;
  
  // Size variants
  &--xxxs {
    width: 12px;
    height: 12px;
    
    .snake:after {
      height: 4px;
      width: 4px;
      margin-left: -16px;
      margin-top: -2px;
    }
  }
  
  &--xxs {
    width: 16px;
    height: 16px;
    
    .snake:after {
      height: 6px;
      width: 6px;
      margin-left: -20px;
      margin-top: -3px;
    }
  }
  
  &--xs {
    width: 20px;
    height: 20px;
    
    .snake:after {
      height: 7px;
      width: 7px;
      margin-left: -24px;
      margin-top: -3.5px;
    }
  }
  
  &--sm {
    width: 25px;
    height: 25px;
    
    .snake:after {
      height: 8px;
      width: 8px;
      margin-left: -28px;
      margin-top: -4px;
    }
  }
  
  &--md {
    width: 30px;
    height: 30px;
    
    .snake:after {
      height: 10px;
      width: 10px;
      margin-left: -32.5px;
      margin-top: -5px;
    }
  }
  
  &--lg {
    width: 40px;
    height: 40px;
    
    .snake:after {
      height: 12px;
      width: 12px;
      margin-left: -40px;
      margin-top: -6px;
    }
  }
  
  &--xl {
    width: 50px;
    height: 50px;
    
    .snake:after {
      height: 15px;
      width: 15px;
      margin-left: -48px;
      margin-top: -7.5px;
    }
  }
}

/**
  * Snake
  *
  * @author jh3y
*/
.snake:after {
  animation: snake 1s infinite both ease;
  border-radius: 5px;
  content: '';
  height: 10px;
  left: 50%;
  margin-left: -32.5px;
  margin-top: -5px;
  position: absolute;
  top: 50%;
  width: 10px;
}

@keyframes snake {
  0%,
  5% {
    box-shadow: 15px 15px 0 -10px var(--primary-500), 30px 15px 0 -10px var(--primary-500), 45px 15px 0 -10px var(--primary-500), 45px 0 0 -10px var(--primary-500), 45px -15px 0 -10px var(--primary-500), 30px -15px 0 -10px var(--primary-500), 15px -15px 0 -10px var(--primary-500), 15px 0 0 -10px var(--primary-500), 30px 0 0 -10px var(--primary-500);
  }

  10% {
    box-shadow: 15px 15px 0 0 var(--primary-500), 30px 15px 0 -10px var(--primary-500), 45px 15px 0 -10px var(--primary-500), 45px 0 0 -10px var(--primary-500), 45px -15px 0 -10px var(--primary-500), 30px -15px 0 -10px var(--primary-500), 15px -15px 0 -10px var(--primary-500), 15px 0 0 -10px var(--primary-500), 30px 0 0 -10px var(--primary-500);
  }

  15% {
    box-shadow: 15px 15px 0 0 var(--primary-500), 30px 15px 0 0 var(--primary-500), 45px 15px 0 -10px var(--primary-500), 45px 0 0 -10px var(--primary-500), 45px -15px 0 -10px var(--primary-500), 30px -15px 0 -10px var(--primary-500), 15px -15px 0 -10px var(--primary-500), 15px 0 0 -10px var(--primary-500), 30px 0 0 -10px var(--primary-500);
  }

  20% {
    box-shadow: 15px 15px 0 0 var(--primary-500), 30px 15px 0 0 var(--primary-500), 45px 15px 0 0 var(--primary-500), 45px 0 0 -10px var(--primary-500), 45px -15px 0 -10px var(--primary-500), 30px -15px 0 -10px var(--primary-500), 15px -15px 0 -10px var(--primary-500), 15px 0 0 -10px var(--primary-500), 30px 0 0 -10px var(--primary-500);
  }

  25% {
    box-shadow: 15px 15px 0 0 var(--primary-500), 30px 15px 0 0 var(--primary-500), 45px 15px 0 0 var(--primary-500), 45px 0 0 0 var(--primary-500), 45px -15px 0 -10px var(--primary-500), 30px -15px 0 -10px var(--primary-500), 15px -15px 0 -10px var(--primary-500), 15px 0 0 -10px var(--primary-500), 30px 0 0 -10px var(--primary-500);
  }

  30% {
    box-shadow: 15px 15px 0 0 var(--primary-500), 30px 15px 0 0 var(--primary-500), 45px 15px 0 0 var(--primary-500), 45px 0 0 0 var(--primary-500), 45px -15px 0 0 var(--primary-500), 30px -15px 0 -10px var(--primary-500), 15px -15px 0 -10px var(--primary-500), 15px 0 0 -10px var(--primary-500), 30px 0 0 -10px var(--primary-500);
  }

  35% {
    box-shadow: 15px 15px 0 0 var(--primary-500), 30px 15px 0 0 var(--primary-500), 45px 15px 0 0 var(--primary-500), 45px 0 0 0 var(--primary-500), 45px -15px 0 0 var(--primary-500), 30px -15px 0 0 var(--primary-500), 15px -15px 0 -10px var(--primary-500), 15px 0 0 -10px var(--primary-500), 30px 0 0 -10px var(--primary-500);
  }

  40% {
    box-shadow: 15px 15px 0 0 var(--primary-500), 30px 15px 0 0 var(--primary-500), 45px 15px 0 0 var(--primary-500), 45px 0 0 0 var(--primary-500), 45px -15px 0 0 var(--primary-500), 30px -15px 0 0 var(--primary-500), 15px -15px 0 0 var(--primary-500), 15px 0 0 -10px var(--primary-500), 30px 0 0 -10px var(--primary-500);
  }

  45% {
    box-shadow: 15px 15px 0 0 var(--primary-500), 30px 15px 0 0 var(--primary-500), 45px 15px 0 0 var(--primary-500), 45px 0 0 0 var(--primary-500), 45px -15px 0 0 var(--primary-500), 30px -15px 0 0 var(--primary-500), 15px -15px 0 0 var(--primary-500), 15px 0 0 0 var(--primary-500), 30px 0 0 -10px var(--primary-500);
  }

  50% {
    box-shadow: 15px 15px 0 0 var(--primary-500), 30px 15px 0 0 var(--primary-500), 45px 15px 0 0 var(--primary-500), 45px 0 0 0 var(--primary-500), 45px -15px 0 0 var(--primary-500), 30px -15px 0 0 var(--primary-500), 15px -15px 0 0 var(--primary-500), 15px 0 0 0 var(--primary-500), 30px 0 0 0 var(--primary-500);
  }

  55% {
    box-shadow: 15px 15px 0 -10px var(--primary-500), 30px 15px 0 0 var(--primary-500), 45px 15px 0 0 var(--primary-500), 45px 0 0 0 var(--primary-500), 45px -15px 0 0 var(--primary-500), 30px -15px 0 0 var(--primary-500), 15px -15px 0 0 var(--primary-500), 15px 0 0 0 var(--primary-500), 30px 0 0 0 var(--primary-500);
  }

  60% {
    box-shadow: 15px 15px 0 -10px var(--primary-500), 30px 15px 0 -10px var(--primary-500), 45px 15px 0 0 var(--primary-500), 45px 0 0 0 var(--primary-500), 45px -15px 0 0 var(--primary-500), 30px -15px 0 0 var(--primary-500), 15px -15px 0 0 var(--primary-500), 15px 0 0 0 var(--primary-500), 30px 0 0 0 var(--primary-500);
  }

  65% {
    box-shadow: 15px 15px 0 -10px var(--primary-500), 30px 15px 0 -10px var(--primary-500), 45px 15px 0 -10px var(--primary-500), 45px 0 0 0 var(--primary-500), 45px -15px 0 0 var(--primary-500), 30px -15px 0 0 var(--primary-500), 15px -15px 0 0 var(--primary-500), 15px 0 0 0 var(--primary-500), 30px 0 0 0 var(--primary-500);
  }

  70% {
    box-shadow: 15px 15px 0 -10px var(--primary-500), 30px 15px 0 -10px var(--primary-500), 45px 15px 0 -10px var(--primary-500), 45px 0 0 -10px var(--primary-500), 45px -15px 0 0 var(--primary-500), 30px -15px 0 0 var(--primary-500), 15px -15px 0 0 var(--primary-500), 15px 0 0 0 var(--primary-500), 30px 0 0 0 var(--primary-500);
  }

  75% {
    box-shadow: 15px 15px 0 -10px var(--primary-500), 30px 15px 0 -10px var(--primary-500), 45px 15px 0 -10px var(--primary-500), 45px 0 0 -10px var(--primary-500), 45px -15px 0 -10px var(--primary-500), 30px -15px 0 0 var(--primary-500), 15px -15px 0 0 var(--primary-500), 15px 0 0 0 var(--primary-500), 30px 0 0 0 var(--primary-500);
  }

  80% {
    box-shadow: 15px 15px 0 -10px var(--primary-500), 30px 15px 0 -10px var(--primary-500), 45px 15px 0 -10px var(--primary-500), 45px 0 0 -10px var(--primary-500), 45px -15px 0 -10px var(--primary-500), 30px -15px 0 -10px var(--primary-500), 15px -15px 0 0 var(--primary-500), 15px 0 0 0 var(--primary-500), 30px 0 0 0 var(--primary-500);
  }

  85% {
    box-shadow: 15px 15px 0 -10px var(--primary-500), 30px 15px 0 -10px var(--primary-500), 45px 15px 0 -10px var(--primary-500), 45px 0 0 -10px var(--primary-500), 45px -15px 0 -10px var(--primary-500), 30px -15px 0 -10px var(--primary-500), 15px -15px 0 -10px var(--primary-500), 15px 0 0 0 var(--primary-500), 30px 0 0 0 var(--primary-500);
  }

  90% {
    box-shadow: 15px 15px 0 -10px var(--primary-500), 30px 15px 0 -10px var(--primary-500), 45px 15px 0 -10px var(--primary-500), 45px 0 0 -10px var(--primary-500), 45px -15px 0 -10px var(--primary-500), 30px -15px 0 -10px var(--primary-500), 15px -15px 0 -10px var(--primary-500), 15px 0 0 -10px var(--primary-500), 30px 0 0 0 var(--primary-500);
  }

  95%,
  100% {
    box-shadow: 15px 15px 0 -10px var(--primary-500), 30px 15px 0 -10px var(--primary-500), 45px 15px 0 -10px var(--primary-500), 45px 0 0 -10px var(--primary-500), 45px -15px 0 -10px var(--primary-500), 30px -15px 0 -10px var(--primary-500), 15px -15px 0 -10px var(--primary-500), 15px 0 0 -10px var(--primary-500), 30px 0 0 -10px var(--primary-500);
  }
}
</style>

<template>
    <div class="hb-color-palette-locked">
        <div class="color-container">
            <!-- Color boxes - all locked except first one shows default color -->
            <div v-for="(color, index) in displayColors" :key="index" class="color-item">
                <HbTooltip 
                    position="right"
                    variant="dark"
                    :delay="200"
                >
                    <template #content>
                        <span class="tooltip-content">This template doesn't support multiple colors</span>
                    </template>
                    <div class="color-swatch" :class="{ locked: index !== 0 }">
                        <div class="color-box" :style="{ backgroundColor: index === 0 ? defaultColor : '#e5e7eb' }">
                            <!-- Check icon for first box -->
                            <div v-if="index === 0" class="check-icon">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                                    <polyline points="20 6 9 17 4 12"></polyline>
                                </svg>
                            </div>
                            <!-- Lock icon for other boxes -->
                            <div v-else class="lock-icon">
                                <svg version="1.1" xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="13px" viewBox="0 0 401.998 401.998">
                                    <path fill="currentColor" d="M357.45,190.721c-5.331-5.33-11.8-7.993-19.417-7.993h-9.131v-54.821c0-35.022-12.559-65.093-37.685-90.218
		C266.093,12.563,236.025,0,200.998,0c-35.026,0-65.1,12.563-90.222,37.688C85.65,62.814,73.091,92.884,73.091,127.907v54.821
		h-9.135c-7.611,0-14.084,2.663-19.414,7.993c-5.33,5.326-7.994,11.799-7.994,19.417V374.59c0,7.611,2.665,14.086,7.994,19.417
		c5.33,5.325,11.803,7.991,19.414,7.991H338.04c7.617,0,14.085-2.663,19.417-7.991c5.325-5.331,7.994-11.806,7.994-19.417V210.135
		C365.455,202.523,362.782,196.051,357.45,190.721z M274.087,182.728H127.909v-54.821c0-20.175,7.139-37.402,21.414-51.675
		c14.277-14.275,31.501-21.411,51.678-21.411c20.179,0,37.399,7.135,51.677,21.411c14.271,14.272,21.409,31.5,21.409,51.675V182.728z"/>
                                </svg>
                            </div>
                        </div>
                    </div>
                </HbTooltip>
            </div>
        </div>


    </div>
</template>

<script setup lang="ts">
// @ts-strict
import { computed } from 'vue';
import HbTooltip from '~/components/base/HbTooltip.vue';

interface Props {
    defaultColor?: string
}

const props = withDefaults(defineProps<Props>(), {
    defaultColor: '#333333'
});

// Always show 6 color boxes
const displayColors = computed<null[]>(() => {
    return Array(6).fill(null);
});
</script>

<style lang="scss" scoped>
.hb-color-palette-locked {
    margin-bottom: 3rem; /* Extra space for tooltip below */
    padding-top: 0.5rem; /* Extra space for tooltip above if needed */
}

.tooltip-content {
    display: inline-block;
    white-space: nowrap;
    max-width: none;
    padding: 2px 4px;
}

/* Override HbTooltip max-width to prevent text cutting */
.color-item :deep(.hb-tooltip) {
    max-width: none !important;
    width: max-content;
}

.color-item :deep(.hb-tooltip__content) {
    white-space: nowrap;
}

.color-container {
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    gap: 12px;
    margin-bottom: 12px;
}

.color-item {
    display: inline-flex;
    align-items: center;
}

.color-swatch {
    position: relative;
    cursor: not-allowed;

    &.locked {
        opacity: 0.7;
    }
}

.color-box {
    height: 32px;
    width: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid;
    border-color: inherit;
    transition: all 0.2s ease;
    position: relative;
}

.lock-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    position: relative;
    z-index: 10;
    color: #333;
}

.check-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    position: relative;
    z-index: 10;
    color: #fff;
   
}

.locked-message {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.875rem;
    color: var(--gray-400);
    margin: 0;
    padding: 12px;
    background: var(--primary-900);
    border-radius: var(--radius-md);
    border: 1px solid var(--primary-800);

    svg {
        flex-shrink: 0;
        color: var(--gray-500);
    }
}

/* Dark theme compatibility */
@media (prefers-color-scheme: dark) {
    .lock-icon {
        color: #9ca3af;

        
    }
}
</style>

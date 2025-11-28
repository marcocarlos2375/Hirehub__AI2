<template>
  <div>
    <div class="min-h-screen py-16 page-with-bg">
      <div class="container mx-auto px-4">
        <div class="card-container-shadow">
          <!-- Loading State -->
          <div v-if="isLoading" class="bg-white py-24 px-8 rounded-lg max-w-7xl mx-auto flex flex-col items-center justify-center min-h-[400px]">
            <HbSpinner size="xl" />
            <p class="text-gray-600 mt-4 font-medium">{{ t('pages.coverLetter.edit.loadingCoverLetter') }}</p>
          </div>

          <!-- Connection Error State -->
          <div v-else-if="hasConnectionError" class="bg-white py-24 px-8 rounded-lg max-w-7xl mx-auto">
            <HbNoConnection
              :title="t('pages.coverLetter.edit.noInternetTitle')"
              :text="t('pages.coverLetter.edit.noInternetText')"
              :button-label="t('pages.coverLetter.edit.retryButton')"
              button-icon="ri-refresh-line"
              @retry="retryLoadCoverLetter"
            />
          </div>

          <!-- Cover Letter Not Found State -->
          <div v-else-if="coverLetterNotFound" class="bg-white py-24 px-8 rounded-lg max-w-7xl mx-auto">
            <HbResumeNotFound
              :title="t('pages.coverLetter.edit.coverLetterNotFoundTitle')"
              :text="t('pages.coverLetter.edit.coverLetterNotFoundText')"
              :button-label="t('pages.coverLetter.edit.goToCoverLettersButton')"
              button-icon="ri-file-list-3-line"
              to="/dashboard/cover-letters"
            />
          </div>

          <!-- Wizard Layout -->
          <div v-else-if="!isLoading && !hasConnectionError && !coverLetterNotFound" class="wizard-layout bg-white rounded-lg max-w-7xl mx-auto">
            
            <!-- Mobile Horizontal Steps (visible only on mobile) -->
            <div class="mobile-steps-header">
              <div class="mobile-steps-title">
                <h2 class="text-white text-xl font-semibold truncate">{{ coverLetterStore.title || t('pages.coverLetter.edit.myCoverLetter') }}</h2>
                <button @click="showMobileActionsMenu = !showMobileActionsMenu" class="mobile-actions-button">
                  <i class="ri-more-2-fill"></i>
                </button>
              </div>

              <!-- Mobile Actions Dropdown -->
              <div v-if="showMobileActionsMenu" class="mobile-actions-menu">
                <div class="mobile-actions-overlay" @click="showMobileActionsMenu = false"></div>
                <div class="mobile-actions-content">
                  <div class="mobile-actions-header">
                    <h3 class="font-semibold text-gray-900">{{ t('pages.coverLetter.edit.actions') }}</h3>
                    <button @click="showMobileActionsMenu = false" class="mobile-actions-close">
                      <i class="ri-close-line"></i>
                    </button>
                  </div>

                  <div class="mobile-actions-list">
                    <!-- HR Advice -->
                    <button @click="showAdviceModal = true; showMobileActionsMenu = false" class="mobile-action-item">
                      <i class="ri-lightbulb-flash-line text-primary-500"></i>
                      <span>{{ t('pages.coverLetter.edit.hrAdvice') }}</span>
                    </button>

                    <!-- Attach Resume -->
                    <button @click="checkAttachResumeAccess" class="mobile-action-item">
                      <i class="ri-file-line text-amber-500"></i>
                      <span>{{ t('pages.coverLetter.edit.attachResume') }}</span>
                      <i v-if="!isPremiumUser" class="ri-vip-crown-line text-amber-400 ml-auto"></i>
                    </button>

                    <!-- AI Customize -->
                    <button @click="checkAICustomizeAccess" class="mobile-action-item">
                      <i class="ri-sparkling-line text-amber-500"></i>
                      <span>{{ t('pages.coverLetter.edit.customizeForJob') }}</span>
                      <i v-if="!isPremiumUser" class="ri-vip-crown-line text-amber-400 ml-auto"></i>
                    </button>

                    <!-- Download -->
                    <button @click="showMobileActionsMenu = false" class="mobile-action-item mobile-action-item--primary">
                      <i class="ri-download-line"></i>
                      <span>{{ t('pages.coverLetter.edit.downloadPdf') }}</span>
                    </button>

                    <!-- Translate -->
                    <button @click="showMobileActionsMenu = false; showLanguageModal = true" class="mobile-action-item">
                      <i class="ri-translate"></i>
                      <span>{{ t('pages.coverLetter.edit.translate') || 'Translate' }}</span>
                    </button>

                    <!-- Save Status -->
                    <div class="mobile-action-status">
                      <div v-if="isSaving" class="flex items-center gap-2">
                        <span class="text-xs saving-shimmer-text">{{ t('pages.coverLetter.edit.saving') }}</span>
                      </div>
                      <HbTooltip
                        v-else-if="hasPendingChanges && saveCountdown > 0"
                        position="bottom"
                        variant="dark"
                        :arrow="true"
                      >
                        <div class="flex items-center gap-2 cursor-pointer">
                          <span class="text-xs saving-shimmer-text">{{ t('pages.coverLetter.edit.saving') }}</span>
                        </div>
                        <template #content>
                          <span class="text-sm font-medium">Saving in {{ (saveCountdown / 1000).toFixed(1) }}s...</span>
                        </template>
                      </HbTooltip>
                      <div v-else class="flex items-center gap-2">
                        <i class="ri-cloud-line text-primary-500"></i>
                        <span class="text-xs text-primary-500">{{ t('pages.coverLetter.edit.saved', { time: calculatedSyncTime }) }}</span>
                      </div>
                      <span class="text-xs text-gray-500">{{ t('pages.coverLetter.edit.percentComplete', { percent: coverLetterStore.completionPercentage }) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="mobile-steps-scroll">
                <div class="mobile-steps-container">
                  <button
                    v-for="wizardStep in wizardSteps"
                    :key="wizardStep.id"
                    @click="navigateToStep(wizardStep.id)"
                    class="mobile-step-item"
                    :class="{
                      'mobile-step-item--active': step === wizardStep.id,
                      'mobile-step-item--completed': step > wizardStep.id,
                      'mobile-step-item--upcoming': step < wizardStep.id
                    }"
                  >
                    <div class="mobile-step-icon">
                      <span v-if="step > wizardStep.id" class="mobile-step-check">
                        <i class="ri-check-line"></i>
                      </span>
                      <span v-else class="mobile-step-number">{{ wizardStep.id - 1 }}</span>
                    </div>
                    <span class="mobile-step-label">{{ wizardStep.title }}</span>
                  </button>
                  <button class="mobile-step-item mobile-step-item--more">
                    <i class="ri-more-line"></i>
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Sidebar -->
            <div class="wizard-sidebar bg-primary-900 text-white" :class="{ 'sidebar-expanded': sidebarExpanded }">
              <div class="p-6">
                <div class="flex items-center justify-between mb-6">
                  <input
                    v-model="coverLetterTitle"
                    @focus="previousTitle = coverLetterStore.title"
                    @blur="saveCoverLetterTitle"
                    @keydown.enter="($event.target as HTMLInputElement).blur()"
                    class="resume-title-input text-lg font-semibold bg-transparent border-none text-white placeholder-white/60 focus:outline-none focus:border-b focus:border-white/40 transition-all"
                    :placeholder="t('pages.coverLetter.edit.coverLetterTitlePlaceholder')"
                    maxlength="50"
                  />
                  
                </div>
                <nav ref="sidebarNav" class="space-y-2 sidebar-nav-scrollable"
                  :class="{ 'nav-expanded': sidebarExpanded }">
                  <div v-for="(wizardStep, index) in visibleSidebarSteps" :key="wizardStep.id"
                    :ref="wizardStep.id === step ? 'activeStep' : undefined" 
                    v-motion
                    :initial="{ opacity: 0, x: -50 }"
                    :enter="{ 
                      opacity: 1, 
                      x: 0,
                      transition: {
                        delay: index * 50,
                        duration: 400,
                        ease: 'easeOut'
                      }
                    }"
                    :tap="!wizardStep.isEllipsis ? { scale: 0.98 } : {}"
                    class="sidebar-step" :class="{
                      'sidebar-step--ellipsis': wizardStep.isEllipsis,
                      'sidebar-step--active': !wizardStep.isEllipsis && step === wizardStep.id,
                      'sidebar-step--completed': !wizardStep.isEllipsis && step > wizardStep.id,
                      'sidebar-step--upcoming': !wizardStep.isEllipsis && step < wizardStep.id
                    }" @click="wizardStep.isEllipsis ? scrollSidebarDown() : navigateToStep(wizardStep.id)">
                    <!-- Ellipsis Item -->
                    <div v-if="wizardStep.isEllipsis"
                      class="flex items-center justify-center p-3 cursor-pointer hover:bg-white/5 rounded-lg transition-all">
                      <div class="text-white/60 text-lg font-medium">•••</div>
                    </div>

                    <!-- Regular Step Item -->
                    <div v-else class="flex items-center gap-3 p-3 rounded-lg transition-all">
                      <div class="step-number">
                        <span v-if="step > wizardStep.id">
                          <i class="ri-check-line"></i>
                        </span>
                        <span v-else>{{ wizardStep.displayIndex }}</span>
                      </div>
                      <div class="step-info">
                        <div class="step-title">{{ wizardStep.title }}</div>
                        <div class="step-subtitle">{{ wizardStep.subtitle }}</div>
                      </div>
                    </div>
                  </div>
                </nav>
              </div>
            </div>

            <!-- Main Content Area -->
            <div class="wizard-content">
              <!-- Fixed Header for all steps -->
              <div class="wizard-step-header">
                <!-- Left: Content Advice & Document Actions -->
                <div class="flex items-center gap-3">
                  <!-- Content advice (first - distinct action) -->
                  <HbButton
                    variant="light"
                    size="sm"
                    rounded="pill"
                    :border="false"
                    @click="showAdviceModal = true"
                  >
                    <template #leading-icon>
                      <i class="ri-lightbulb-flash-line"></i>
                    </template>
                    <span class="hidden sm:inline">{{ t('pages.coverLetter.edit.hrAdvice') }}</span>
                  </HbButton>

                  <!-- Separator -->
                  <div class="hidden sm:block h-6 w-px bg-primary-100"></div>

                  <!-- PDF-related actions (grouped together) -->
                  <div class="flex items-center gap-1">
                    <HbButton
                      variant="transparent"
                      size="sm"
                      @click="showLanguageModal = true"
                    >
                      <template #leading-icon>
                        <i class="ri-translate"></i>
                      </template>
                      <span class="hidden sm:inline">{{ t('pages.coverLetter.edit.translate') || 'Translate' }}</span>
                    </HbButton>

                    <!-- Version History Button -->
                    <HbButton
                      variant="transparent"
                      size="sm"
                      @click="showHistoryModal = true"
                    >
                      <template #leading-icon>
                        <i class="ri-history-line"></i>
                      </template>
                      <span class="hidden sm:inline">History</span>
                    </HbButton>

                    <!-- Preview Button -->
                    <HbButton
                      variant="ghost"
                      size="sm"
                      rounded="pill"
                      :border="false"
                      @click="openPreviewModal"
                    >
                      <template #leading-icon>
                        <i class="ri-eye-line"></i>
                      </template>
                      <span class="hidden sm:inline">Preview</span>
                    </HbButton>
                  </div>
                </div>

                <!-- Right: Primary Actions + Status -->
                <div class="flex items-center gap-3">
                  <HbButton
                    variant="light-gray"
                    size="sm"
                    :border="false"
                    @click="checkAttachResumeAccess"
                  >
                    <template #leading-icon>
                      <i class="ri-file-line text-amber-500"></i>
                    </template>
                    <span class="hidden md:inline">{{ t('pages.coverLetter.edit.attachResume') }}</span>
                    <span class="inline md:hidden">{{ t('pages.coverLetter.edit.attachResume') }}</span>
                  </HbButton>
                  <!-- AI Customize Button -->
                  <HbButton
                    variant="light-gray"
                    size="sm"
                    :border="false"
                    @click="checkAICustomizeAccess"
                  >
                    <template #leading-icon>
                      <i class="ri-sparkling-line text-amber-500"></i>
                    </template>
                    <span class="hidden md:inline">{{ t('pages.coverLetter.edit.customizeForJob') }}</span>
                    <span class="inline md:hidden">{{ t('pages.coverLetter.edit.aiCustomize') }}</span>
                  </HbButton>

                  <!-- Download Button -->
                  <HbButton
                    variant="primary"
                    size="sm"
                  >
                    {{ t('pages.coverLetter.edit.download') }}
                  </HbButton>
                  
                  <!-- Divider -->
                  <div class="hidden sm:block h-6 w-px bg-primary-200/30"></div>
                  
                  <!-- Save Status -->
                  <div class="save-status">
                    <div v-if="isSaving" class="flex items-center gap-2">
                    <span class="text-xs saving-shimmer-text">{{ t('pages.coverLetter.edit.saving') }}</span>
                  </div>
                  <HbTooltip
                    v-else-if="hasPendingChanges && saveCountdown > 0"
                    position="bottom"
                    variant="dark"
                    :arrow="true"
                  >
                    <div class="flex items-center gap-2 cursor-pointer">
                      <span class="text-xs saving-shimmer-text">{{ t('pages.coverLetter.edit.saving') }}</span>
                    </div>
                    <template #content>
                      <span class="text-sm font-medium">Saving in {{ (saveCountdown / 1000).toFixed(1) }}s...</span>
                    </template>
                  </HbTooltip>
                  <HbTooltip
                    v-else
                    position="bottom"
                    variant="dark"
                    :arrow="true"
                  >
                    <div
                      class="flex items-center gap-2 cursor-pointer"
                      @mouseenter="handleTimezoneTooltipShow"
                    >
                      <i class="ri-cloud-line text-primary-500"></i>
                      <span class="text-xs text-primary-500">{{ t('pages.coverLetter.edit.savedShort') }}</span>
                    </div>
                    <template #content>
                      <div v-if="isCalculatingTimezone" class="sync-tooltip-content">
                        <div class="flex items-center justify-center gap-2 py-2">
                          <HbSpinner size="xs" />
                          <span class="sync-tooltip-label">{{ t('pages.coverLetter.edit.calculatingTimezone') }}</span>
                        </div>
                      </div>
                      <div v-else class="sync-tooltip-content">
                        <div class="sync-tooltip-row">
                          <span class="sync-tooltip-label">{{ t('pages.coverLetter.edit.tooltipStatus') }}</span>
                          <span class="sync-tooltip-value">{{ t('pages.coverLetter.edit.synced') }}</span>
                        </div>
                        <div v-if="coverLetterStore.lastSyncedAt" class="sync-tooltip-row">
                          <span class="sync-tooltip-label">{{ t('pages.coverLetter.edit.lastSync') }}</span>
                          <span class="sync-tooltip-value">{{ calculatedSyncTime }}</span>
                        </div>
                        <div v-if="coverLetterStore.lastSyncedAt" class="sync-tooltip-row">
                          <span class="sync-tooltip-label">{{ t('pages.coverLetter.edit.fullDate') }}</span>
                          <span class="sync-tooltip-value">{{ coverLetterStore.absoluteLastSyncTime }}</span>
                        </div>
                        <div class="sync-tooltip-row">
                          <span class="sync-tooltip-label">{{ t('pages.coverLetter.edit.completion') }}</span>
                          <span class="sync-tooltip-value">{{ coverLetterStore.completionPercentage }}%</span>
                        </div>
                        <div v-if="!coverLetterStore.lastSyncedAt" class="sync-tooltip-row">
                          <span class="sync-tooltip-value">{{ t('pages.coverLetter.edit.notSyncedYet') }}</span>
                        </div>
                      </div>
                    </template>
                  </HbTooltip>
                  </div>
                </div>
              </div>

              <!-- Step 2: Processing/Skeleton Animation -->
              <div 
                v-if="step === 2" 
                :key="step" 
                class="wizard-step-content-animated"
              >
                <div class="wizard-step-content">
                  <div class="mb-8">
                    <h3 class="text-2xl font-semibold text-gray-900 mb-2">{{ stepContent[2].title }}</h3>
                    <p class="text-sm text-gray-600">{{ stepContent[2].subtitle }}</p>
                  </div>

                  <!-- Skeleton Animation -->
                  <div class="space-y-6">
                    <div class="flex items-center gap-4">
                      <div class="skeleton-box w-20 h-20 rounded-full flex-shrink-0"></div>
                      <div class="flex-1 space-y-3">
                        <div class="skeleton-box h-4 w-3/4 rounded"></div>
                        <div class="skeleton-box h-3 w-1/2 rounded"></div>
                        <div class="skeleton-box h-3 w-2/3 rounded"></div>
                      </div>
                    </div>

                    <div class="space-y-3">
                      <div class="skeleton-box h-5 w-32 rounded"></div>
                      <div class="skeleton-box h-20 rounded-lg"></div>
                    </div>

                    <div class="space-y-3">
                      <div class="skeleton-box h-5 w-24 rounded"></div>
                      <div class="flex flex-wrap gap-2">
                        <div class="skeleton-box h-8 w-20 rounded-full"></div>
                        <div class="skeleton-box h-8 w-24 rounded-full"></div>
                        <div class="skeleton-box h-8 w-28 rounded-full"></div>
                        <div class="skeleton-box h-8 w-20 rounded-full"></div>
                        <div class="skeleton-box h-8 w-32 rounded-full"></div>
                        <div class="skeleton-box h-8 w-24 rounded-full"></div>
                      </div>
                    </div>

                    <div class="space-y-3">
                      <div class="skeleton-box h-5 w-36 rounded"></div>
                      <div class="skeleton-box h-24 rounded-lg"></div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Steps 3-6: Core Form Steps -->
              <div 
                v-else-if="step >= 3 && step <= 6" 
                :key="'core-' + step" 
                class="wizard-step-content-animated"
                v-motion
                :initial="step === 3 ? { opacity: 0, scale: 0.95 } : { opacity: 1, scale: 1 }"
                :enter="{ 
                  opacity: 1, 
                  scale: 1,
                  transition: {
                    duration: step === 3 ? 400 : 0,
                    ease: 'easeOut'
                  }
                }"
              >
                <div class="wizard-step-content">
                  <div class="mb-6 flex items-start justify-between gap-4">
                    <div class="flex-1">
                      <h3 class="text-2xl font-semibold text-gray-900 mb-2">{{ currentWizardStep.title }}</h3>
                      <p class="text-sm text-gray-600">{{ currentWizardStep.subtitle }}</p>
                    </div>
                    
                  </div>

                  <!-- Render component for all steps -->
                  <div>
                    <component 
                      :is="currentWizardStep.component" 
                      ref="currentStepComponent"
                    />
                  </div>
                </div>
              </div>

              <!-- Steps 7: Signature -->
              <div 
                v-else-if="step === 7" 
                :key="'signature-' + step" 
                class="wizard-step-content-animated"
              >
                <div class="wizard-step-content">
                  <div class="mb-6 flex items-start justify-between gap-4">
                    <div class="flex-1">
                      <h3 class="text-2xl font-semibold text-gray-900 mb-2">{{ currentWizardStep.title }}</h3>
                      <p class="text-sm text-gray-600">{{ currentWizardStep.subtitle }}</p>
                    </div>
                  </div>

                  <!-- Render component for signature -->
                  <div>
                    <component 
                      :is="currentWizardStep.component" 
                      ref="currentStepComponent"
                    />
                  </div>
                </div>
              </div>

              <div
                v-else-if="step === 9"
                class="wizard-step-content-animated"
              >
                <div class="wizard-step-content p-0">
                  <!-- Preview Layout: Left Info, Right Preview -->
                  <div class="preview-final-layout">
                    <!-- Left: Template Info & Actions -->
                    <div class="preview-final-info">
                      <!-- Great Choice Message -->
                      <div class="preview-choice-header">
                        <div class="flex items-center gap-3 mb-4">
                          
                          <div>
                            <h3 class="text-3xl font-semibold text-gray-900">Great Choice!</h3>
                            <p class="text-sm text-gray-600">Your cover letter looks amazing</p>
                          </div>
                        </div>
                      </div>

                      <!-- Template Characteristics -->
                      <div class="template-characteristics">
                        <h4 class="text-sm font-semibold text-gray-900 mb-3">Template Features</h4>
                        <div class="space-y-2">
                          <div class="flex items-start gap-2">
                            <i class="ri-check-line text-primary-500 mt-0.5 flex-shrink-0"></i>
                            <span class="text-sm text-gray-700">Modern & Clean Design</span>
                          </div>
                          <div class="flex items-start gap-2">
                            <i class="ri-check-line text-primary-500 mt-0.5 flex-shrink-0"></i>
                            <span class="text-sm text-gray-700">ATS-Friendly Format</span>
                          </div>
                          <div class="flex items-start gap-2">
                            <i class="ri-check-line text-primary-500 mt-0.5 flex-shrink-0"></i>
                            <span class="text-sm text-gray-700">Professional Typography</span>
                          </div>
                          <div class="flex items-start gap-2">
                            <i class="ri-check-line text-primary-500 mt-0.5 flex-shrink-0"></i>
                            <span class="text-sm text-gray-700">Optimized Spacing</span>
                          </div>
                        </div>
                      </div>

                      <!-- Premium Template Notice - Only show for premium templates -->
                      <div v-if="isCurrentTemplatePremium" class="premium-notice">
                        <div class="flex items-start gap-3 p-4  rounded-lg">
                          <div>
                          <i class="ri-vip-crown-line text-2xl text-amber-400 flex-shrink-0 mt-0.5"></i>

                            <h5 class="font-semibold text-gray-900 text-md mb-1">You selected a Premium Template</h5>
                            <p class="text-xs text-gray-600 mb-3">
                              This template is part of our Premium collection. How would you like to continue?
                            </p>
                            
                            <!-- Action Buttons -->
                            <div class="space-y-2">
                              <HbButton 
                                variant="primary" 
                                class="w-full"
                                @click="$router.push('/settings/billing/upgrade')"
                              >
                                Upgrade to Premium
                              </HbButton>
                              
                              <HbButton 
                                variant="outline" 
                                class="w-full"
                                @click="openCustomizeWithFreeFilter"
                              >
                                
                                Choose Free Template
                              </HbButton>
                            </div>
                          </div>
                        </div>
                      </div>

                    
                    </div>

                    <!-- Right: Template Preview (Removed) -->
                    <div class="preview-final-display">
                      <div class="p-8 bg-gray-50 rounded-lg text-center">
                        <i class="ri-file-text-line text-6xl text-gray-400 mb-4"></i>
                        <p class="text-gray-600 font-medium mb-2">{{ t('pages.coverLetter.edit.previewCompleted') }}</p>
                        <p class="text-gray-500 text-sm">{{ t('pages.coverLetter.edit.previewCompletedDesc') }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Fixed Footer for all steps -->
              <div v-if="step >= 3" class="wizard-step-footer">
                <HbButton variant="ghost" @click="previousStep" :disabled="step === 3">
                  <template #leading-icon>
                    <i class="ri-arrow-left-line"></i>
                  </template>
                  {{ t('pages.coverLetter.edit.previous') }}
                </HbButton>

                <HbButton variant="primary" @click="nextStep">
                  <template v-if="step === finalStep">
                    {{ t('pages.coverLetter.edit.finish') }}
                  </template>
                  <template v-else>
                    {{ t('pages.coverLetter.edit.next') }}
                  </template>
                  <template v-if="step !== finalStep" #trailing-icon>
                    <i class="ri-arrow-right-line"></i>
                  </template>
                </HbButton>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Advice Modal -->
    <HbModal :modelValue="showAdviceModal" @update:modelValue="showAdviceModal = $event"
      :title="t('pages.coverLetter.edit.modals.advice.title')" size="lg">
      <div class="space-y-6">
        <div v-if="currentStepAdvice" class="bg-primary-50  p-4 rounded-lg">
          <div class="flex items-start gap-3">
            <i class="ri-lightbulb-flash-line text-primary-400 text-2xl flex-shrink-0 mt-1"></i>
            <div>
              <h4 class="font-semibold text-gray-900 mb-2">{{ currentStepAdvice.title }}</h4>
              <p class="text-sm text-gray-700 leading-relaxed">{{ currentStepAdvice.description }}</p>
            </div>
          </div>
        </div>

        <div v-if="currentStepAdvice?.tips && currentStepAdvice.tips.length > 0" class="space-y-4">
          <h5 class="font-semibold text-gray-900 text-sm uppercase tracking-wide">{{ t('pages.coverLetter.edit.modals.advice.quickTips') }}</h5>
          <ul class="space-y-3">
            <li v-for="(tip, index) in currentStepAdvice.tips" :key="index" class="flex items-start gap-3">
              <div class="flex-shrink-0 w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center mt-0.5">
                <span class="text-primary-600 text-xs font-semibold">{{ index + 1 }}</span>
              </div>
              <p class="text-sm text-gray-700 flex-1">{{ tip }}</p>
            </li>
          </ul>
        </div>

        <div v-if="currentStepAdvice?.examples && currentStepAdvice.examples.length > 0" class="bg-gray-50 p-4 rounded-lg">
          <h5 class="font-semibold text-gray-900 text-sm mb-3">{{ t('pages.coverLetter.edit.modals.advice.examples') }}</h5>
          <ul class="space-y-2">
            <li v-for="(example, index) in currentStepAdvice.examples" :key="index"
              class="text-sm text-gray-700 flex items-start gap-2">
              <i class="ri-check-line text-primary-400 flex-shrink-0 mt-0.5"></i>
              <span>{{ example }}</span>
            </li>
          </ul>
        </div>
      </div>

      <template #footer>
        <HbButton variant="primary" rounded="pill" size="sm" @click="showAdviceModal = false">
          {{ t('pages.coverLetter.edit.modals.advice.gotIt') }}
        </HbButton>
      </template>
    </HbModal>

    <!-- Job Customize Modal Component -->
    <JobCustomizeModal
      v-model:showJobCustomizeModal="showJobCustomizeModal"
      @job-customized="handleJobCustomized"
    />

    <!-- Upgrade to Premium Modal -->
    <HbUpgradeNow 
      v-model="showUpgradeModal"
      title="Upgrade to Premium"
      modal-title="Unlock Premium Features"
      modal-description="This feature is only available for Premium users. Upgrade now to access AI-powered optimization, premium templates, and unlimited exports."
      :features="[
        'Unlimited Resume Generations',
        'Unlimited Cover Letter Generations',
        'All Premium Templates',
        'AI-Powered Optimization',
        'AI Profile Picture Generator',
        'Attach Resume to Cover Letter',
        'Job Application Tracker',
        'Priority Support'
      ]"
      upgrade-text="Upgrade to Premium"
      cancel-text="Maybe Later"
    />

    <!-- Language Selection Modal -->
    <HbModal
      v-model="showLanguageModal"
      :title="t('pages.coverLetter.edit.languageModal.title')"
      size="sm"
      :show-close-button="true"
    >
      <!-- Explanatory text -->
      <div class="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-100">
        <p class="text-sm text-gray-700 mb-2">
          {{ t('pages.coverLetter.edit.languageModal.description') }}
        </p>
        <NuxtLink
          to="/settings/profile"
          class="text-sm text-primary-500 hover:text-primary-600 font-medium inline-flex items-center gap-1"
        >
          <i class="ri-settings-3-line"></i>
          {{ t('pages.coverLetter.edit.languageModal.changeGlobally') }}
          <i class="ri-arrow-right-up-line"></i>
        </NuxtLink>
      </div>

      <!-- Language list -->
      <div class="language-list space-y-2">
        <button
          v-for="lang in availableLanguages"
          :key="lang.code"
          @click="selectedLanguage = lang.code; showLanguageModal = false"
          class="language-item w-full flex items-center gap-3 p-3 rounded-lg transition-all"
          :class="{
            'bg-gray-100': selectedLanguage === lang.code,
            'hover:bg-gray-50': selectedLanguage !== lang.code
          }"
        >
          <HbIcon :name="lang.code" class="w-6 h-6" />
          <span class="font-medium">{{ lang.nativeName }}</span>
          <i v-if="selectedLanguage === lang.code" class="ri-check-line ml-auto text-primary-500"></i>
        </button>
      </div>
    </HbModal>

    <!-- Version History Modal -->
    <VersionHistoryModal v-model="showHistoryModal" :cover-letter-store="coverLetterStore" />

    <!-- Cover Letter Preview Modal -->
    <CoverLetterPreviewModal
      :modelValue="showPreviewModal"
      @update:modelValue="showPreviewModal = $event"
      :coverLetterToken="coverLetterToken"
    />
  </div>
</template>

<script lang="ts">
// @ts-strict
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCoverLetterStore } from '~/stores/coverLetter'
// Removed: import { useCoverLetterSettingsStore } from '~/stores/coverLetterSettings'
import { useUserStore } from '~/stores/user'
import HbButton from '~/components/base/HbButton.vue'
import HbModal from '~/components/base/HbModal.vue'
import HbModalFullscreen from '~/components/base/HbModalFullscreen.vue'
import HbUpgradeNow from '~/components/base/HbUpgradeNow.vue'
import HbTooltip from '~/components/base/HbTooltip.vue'
import HbSpinner from '~/components/base/HbSpinner.vue'
import HbInput from '~/components/base/HbInput.vue'
import HbNoConnection from '~/components/base/HbNoConnection.vue'
import HbResumeNotFound from '~/components/base/HbResumeNotFound.vue'
import { getTemplateId, getTemplateTags } from '~/config/templateConfig'
import SenderInformation from '~/components/tunnel/SenderInformation.vue'
import RecipientInformation from '~/components/tunnel/RecipientInformation.vue'
import PositionInformation from '~/components/tunnel/PositionInformation.vue'
import LetterContent from '~/components/tunnel/LetterContent.vue'
import LetterSignature from '~/components/tunnel/LetterSignature.vue'
import JobCustomizeModal from '~/components/coverLetter/JobCustomizeModal.vue'
import VersionHistoryModal from '~/components/coverLetter/VersionHistoryModal.vue'
import CoverLetterPreviewModal from '~/components/coverLetter/CoverLetterPreviewModal.vue'
import HbIcon from '~/components/base/HbIcon.vue'

interface WizardStep {
  id: number
  title: string
  subtitle: string
  component: string | null
  displayIndex?: number
  isEllipsis?: boolean
}

interface StepContent {
  title: string
  subtitle: string
}

interface StepAdvice {
  title: string
  description: string
  tips: string[]
  examples?: string[]
}

interface LanguageOption {
  code: string
  nativeName: string
}

export default {
  name: 'CoverLetterEdit',
  components: {
    HbButton,
    HbModal,
    HbModalFullscreen,
    HbUpgradeNow,
    HbIcon,
    HbTooltip,
    HbSpinner,
    HbInput,
    HbNoConnection,
    HbResumeNotFound,
    SenderInformation,
    RecipientInformation,
    PositionInformation,
    LetterContent,
    LetterSignature,
    JobCustomizeModal,
    VersionHistoryModal,
    CoverLetterPreviewModal
  },
  
  setup() {
    const { t, locale } = useI18n()
    const coverLetterStore = useCoverLetterStore()
    const userStore = useUserStore()
    return { t, locale, coverLetterStore, userStore }
  },
  
  provide() {
    return {
      // Settings have been removed - templates will need to be updated
      coverLetterSettings: computed(() => null)
    }
  },

  data(): {
    coverLetterToken: string | null
    isLoading: boolean
    hasConnectionError: boolean
    coverLetterNotFound: boolean
    selectedTemplate: string
    isTemplateLoading: boolean
    showTemplatePlaceholder: boolean
    settingsLoaded: boolean
    previewRefreshKey: number
    step: number
    renderKey: number
    sidebarExpanded: boolean
    isSaving: boolean
    showAdviceModal: boolean
    showJobCustomizeModal: boolean
    showMobileActionsMenu: boolean
    showUpgradeModal: boolean
    showLanguageModal: boolean
    showHistoryModal: boolean
    showPreviewModal: boolean
    availableLanguages: LanguageOption[]
    isDownloading: boolean
    autoSaveTimer: ReturnType<typeof setTimeout> | null
    periodicSyncTimer: ReturnType<typeof setInterval> | null
    lastSyncedDataHash: string | null
    lastSyncedPayload: any
    isComponentActive: boolean
    isCalculatingTimezone: boolean
    currentTime: number
    timeUpdateInterval: ReturnType<typeof setInterval> | null
    previousTitle: string
    previewCurrentPage: number
    previewTotalPages: number
    saveCountdown: number
    countdownInterval: ReturnType<typeof setInterval> | null
    hasPendingChanges: boolean
    isInitialDataLoad: boolean
    lastSnapshotTime: number
    versionPollingTimer: ReturnType<typeof setInterval> | null
    serverVersion: string | null
    isCheckingVersion: boolean
  } {
    return {
      coverLetterToken: null,
      isLoading: true,
      isInitialDataLoad: true, // Flag to prevent watcher from triggering during initial load
      hasConnectionError: false,
      coverLetterNotFound: false,
      selectedTemplate: 'classic', // Default template
      isTemplateLoading: true,
      showTemplatePlaceholder: true,
      settingsLoaded: false, // Track if settings have been loaded from DB
      previewRefreshKey: 0, // Force preview component re-render
      step: 2,
      renderKey: 0, // Force re-render when changed
      sidebarExpanded: false,
      isSaving: false,
      showAdviceModal: false,
      showJobCustomizeModal: false,
      showMobileActionsMenu: false,
      showUpgradeModal: false, // Premium upgrade modal
      showLanguageModal: false, // Language selection modal
      showHistoryModal: false, // Version history modal
      showPreviewModal: false, // Preview modal
      availableLanguages: [
        { code: 'english', nativeName: 'English' },
        { code: 'french', nativeName: 'Français' },
        { code: 'german', nativeName: 'Deutsch' },
        { code: 'spanish', nativeName: 'Español' }
      ],
      isDownloading: false,
      autoSaveTimer: null,
      periodicSyncTimer: null,
      lastSyncedDataHash: null, // Track last synced data to detect changes
      versionPollingTimer: null, // Interval for checking server version (cross-browser sync)
      serverVersion: null, // Last known server version timestamp
      isCheckingVersion: false, // Track if version check is in progress
      lastSyncedPayload: null as any, // Track last synced payload for snapshot descriptions
      isComponentActive: true, // Track if component is still mounted
      isCalculatingTimezone: false, // Track timezone calculation state
      currentTime: Date.now(), // Force reactivity for time calculations
      timeUpdateInterval: null, // Interval to update current time
      previousTitle: '', // Track previous title to detect changes
      previewCurrentPage: 1, // Current page in final preview
      previewTotalPages: 1, // Total pages in final preview
      saveCountdown: 0, // Countdown timer for auto-save (in ms)
      countdownInterval: null, // Interval for countdown timer
      hasPendingChanges: false, // Track if changes are waiting to be saved
      lastSnapshotTime: 0 // Track when last snapshot was saved (for smart interval-based snapshots)
    }
  },

  computed: {
    stepAdvice(): Record<number, StepAdvice> {
      try {
        // Return advice data from translations using $t method to get actual text values
        const advice: Record<number, StepAdvice> = {}

        // Build advice for each step (3-7 for cover letter editor) using $t to get translated text
        for (let step = 3; step <= 7; step++) {
          const stepKey = String(step)
          const basePath = `pages.coverLetter.edit.modals.advice.steps.${stepKey}`

          // Check if this step has translations
          const title = this.$t(`${basePath}.title`) as string

          // Skip if translation key is returned as-is (means translation doesn't exist)
          if (title === `${basePath}.title`) {
            continue
          }

          const description = this.$t(`${basePath}.description`) as string

          // Get tips array
          const tips: string[] = []
          let tipIndex = 0
          while (true) {
            const tip = this.$t(`${basePath}.tips.${tipIndex}`) as string
            if (tip === `${basePath}.tips.${tipIndex}`) {
              break // No more tips
            }
            tips.push(tip)
            tipIndex++
          }

          // Get examples array
          const examples: string[] = []
          let exampleIndex = 0
          while (true) {
            const example = this.$t(`${basePath}.examples.${exampleIndex}`) as string
            if (example === `${basePath}.examples.${exampleIndex}`) {
              break // No more examples
            }
            examples.push(example)
            exampleIndex++
          }

          advice[step] = {
            title,
            description,
            tips,
            examples
          }
        }

        return advice
      } catch (error) {
        return {}
      }
    },

    stepContent(): Record<number, StepContent> {
      return {
        2: {
          title: this.t('pages.coverLetter.edit.steps.processing.title'),
          subtitle: this.t('pages.coverLetter.edit.steps.processing.subtitle')
        }
      }
    },

    // Get/set selected language from cover letter store
    selectedLanguage: {
      get(): string {
        // Return language from store, fallback to system locale
        const storeLanguage: string | undefined = this.coverLetterStore.language
        if (storeLanguage && storeLanguage !== 'english') {
          return storeLanguage
        }

        // Map system locale to our language codes
        const localeMap: Record<string, string> = {
          'en': 'english',
          'fr': 'french',
          'de': 'german',
          'es': 'spanish'
        }
        return localeMap[this.locale] || 'english'
      },
      set(value: string): void {
        // Update store when language changes
        this.coverLetterStore.language = value
      }
    },

    // Get/set cover letter title from store
    // ✅ Two-way computed property for proper mutations through store action
    coverLetterTitle: {
      get(): string {
        return this.coverLetterStore.title
      },
      set(value: string): void {
        this.coverLetterStore.updateTitle(value)
      }
    },

    coreSteps(): WizardStep[] {
      return [
        {
          id: 3,
          title: this.t('pages.coverLetter.edit.steps.yourInformation.title'),
          subtitle: this.t('pages.coverLetter.edit.steps.yourInformation.subtitle'),
          component: 'SenderInformation'
        },
        {
          id: 4,
          title: this.t('pages.coverLetter.edit.steps.recipientInformation.title'),
          subtitle: this.t('pages.coverLetter.edit.steps.recipientInformation.subtitle'),
          component: 'RecipientInformation'
        },
        {
          id: 5,
          title: this.t('pages.coverLetter.edit.steps.positionDetails.title'),
          subtitle: this.t('pages.coverLetter.edit.steps.positionDetails.subtitle'),
          component: 'PositionInformation'
        },
        {
          id: 6,
          title: this.t('pages.coverLetter.edit.steps.letterContent.title'),
          subtitle: this.t('pages.coverLetter.edit.steps.letterContent.subtitle'),
          component: 'LetterContent'
        },
        {
          id: 7,
          title: this.t('pages.coverLetter.edit.steps.addSignature.title'),
          subtitle: this.t('pages.coverLetter.edit.steps.addSignature.subtitle'),
          component: 'LetterSignature'
        }
      ]
    },

    wizardSteps(): WizardStep[] {
      const steps: WizardStep[] = [...this.coreSteps]

      // Add Template Selection step
      steps.push({
        id: 8,
        title: this.t('pages.coverLetter.edit.steps.chooseTemplate.title'),
        subtitle: this.t('pages.coverLetter.edit.steps.chooseTemplate.subtitle'),
        component: 'TemplateSelection'
      })

      // Add Preview step
      steps.push({
        id: 9,
        title: this.t('pages.coverLetter.edit.steps.preview.title'),
        subtitle: this.t('pages.coverLetter.edit.steps.preview.subtitle'),
        component: 'CoverLetterPreview'
      })

      return steps
    },

    currentWizardStep(): WizardStep {
      return this.wizardSteps.find((s: WizardStep) => s.id === this.step) || this.wizardSteps[0]
    },

    currentStepAdvice(): StepAdvice | null {
      const advice: StepAdvice | null = this.stepAdvice[this.step] || null
      console.log('Current step:', this.step, 'Current advice:', advice)
      return advice
    },

    totalSteps(): number {
      return this.wizardSteps.length
    },

    finalStep(): number {
      return this.wizardSteps[this.wizardSteps.length - 1].id
    },

    visibleSidebarSteps(): WizardStep[] {
      const steps: WizardStep[] = this.wizardSteps
      const totalSteps: number = steps.length
      const maxVisible: number = 9

      if (totalSteps <= maxVisible) {
        return steps.map((step, index) => ({
          ...step,
          displayIndex: index + 1,
          isEllipsis: false
        }))
      }

      const visible = []
      for (let i = 0; i < maxVisible - 1; i++) {
        visible.push({
          ...steps[i],
          displayIndex: i + 1,
          isEllipsis: false
        })
      }

      visible.push({
        id: 'ellipsis-more',
        isEllipsis: true,
        displayIndex: '...'
      })

      return visible
    },
    
    // Real-time calculated sync time that updates
    calculatedSyncTime(): string {
      // Force recalculation by using currentTime
      this.currentTime
      
      if (!this.coverLetterStore.lastSyncedAt) {
        return 'Never synced'
      }
      
      const syncDate = new Date(this.coverLetterStore.lastSyncedAt)
      const now = new Date()
      const diffMs = now.getTime() - syncDate.getTime()
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)

      // Show relative time for recent syncs
      if (diffMins < 1) {
        return 'Just now'
      } else if (diffMins < 60) {
        return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
      } else if (diffHours < 24) {
        return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
      } else if (diffDays < 7) {
        return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
      } else {
        return syncDate.toLocaleString()
      }
    },
    
    // Template key that changes when template changes (forces repagination)
    templateRenderKey(): string {
      return `${this.selectedTemplate}-${this.renderKey}`
    },

    // Check if current template is premium
    isCurrentTemplatePremium(): boolean {
      if (!this.selectedTemplate) return false
      const tags: string[] = getTemplateTags(this.selectedTemplate)
      return tags.includes('premium')
    },

    // Check if user has premium subscription
    isPremiumUser(): boolean {
      const subscriptionType: string | undefined = this.userStore.user?.currentSubscriptionType
      const isPremium: boolean = subscriptionType !== undefined && subscriptionType !== 'free'
      return isPremium
    },

  },
  
  watch: {
   
    
  

    
    // Watch for step 9 to initialize template rendering
    step: {
      handler(newStep, oldStep) {
        if (newStep === 9) {
          // Force template re-render by toggling loading state
          this.isTemplateLoading = true
          this.showTemplatePlaceholder = true
          
          this.$nextTick(() => {
            // Reset after a brief moment to trigger fresh render
            setTimeout(() => {
              this.isTemplateLoading = false
              this.showTemplatePlaceholder = false
            }, 100)
          })
        }
      },
      immediate: true
    },

  },
  
  
  async mounted() {
    // 📊 PERFORMANCE MONITORING: Start
    performance.mark('cover-letter-edit-mount-start')
    console.log('📊 [Performance] Cover letter edit page mounting...')

    // Get token from URL query parameter
    const tokenParam = this.$route.query.token
    this.coverLetterToken = Array.isArray(tokenParam) ? tokenParam[0] : (tokenParam || null)

    if (!this.coverLetterToken) {
      // @ts-expect-error - $notify is injected by plugin
      this.$notify?.error('No cover letter token found', 'Redirecting...')
      this.$router.push('/cover-letter/start')
      return
    }

    // CRITICAL: Set current cover letter token in store FIRST
    // This ensures all components will use the correct token-based data
    // Store loads data from localStorage immediately (synchronous, instant)
    this.coverLetterStore.setCurrentCoverLetter(this.coverLetterToken)
    performance.mark('cover-letter-store-set')

    // PERFORMANCE FIX: Show editor IMMEDIATELY with localStorage data
    // Editor becomes interactive instantly, API data loads in background
    this.step = 3

    // Load fresh data from API in background (no await - non-blocking)
    // When data arrives, store will update and editor will refresh
    this.loadCoverLetterData().then(() => {
      performance.mark('cover-letter-data-loaded')
      console.log('📊 [Performance] Cover letter data loaded from API')

      // Load selected template from cover letter store
      if (this.coverLetterStore.selectedTemplate) {
        this.selectedTemplate = this.coverLetterStore.selectedTemplate
        console.log('📋 Loaded template from cover letter store:', this.selectedTemplate)
      }

      // Mark initial data load as complete - watcher can now trigger auto-save
      // Use $nextTick to ensure DOM updates from data loading complete first
      this.$nextTick(() => {
        this.isInitialDataLoad = false
        console.log('✅ Initial data load complete - auto-save enabled')
      })
    })

    // 📊 PERFORMANCE MONITORING: End
    performance.mark('cover-letter-interactive')
    performance.measure('Total Mount Time', 'cover-letter-edit-mount-start', 'cover-letter-interactive')
    performance.measure('Store Setup Time', 'cover-letter-edit-mount-start', 'cover-letter-store-set')
    performance.measure('Data Load Time', 'cover-letter-store-set', 'cover-letter-data-loaded')
    performance.measure('UI Ready Time', 'cover-letter-data-loaded', 'cover-letter-interactive')

    const measurements = performance.getEntriesByType('measure')
    console.log('📊 [Performance] Cover Letter Edit Page Metrics:')
    measurements.forEach(measure => {
      if (measure.name.includes('Time')) {
        console.log(`  ${measure.name}: ${measure.duration.toFixed(0)}ms`)
      }
    })

    // Watch for changes in cover letter store to auto-save
    // Only watch the actual content fields, not internal state like history
    this.$watch(
      () => ({
        senderInfo: this.coverLetterStore.senderInfo,
        recipientInfo: this.coverLetterStore.recipientInfo,
        positionInfo: this.coverLetterStore.positionInfo,
        letterContent: this.coverLetterStore.letterContent,
        language: this.coverLetterStore.language,
        title: this.coverLetterStore.title
      }),
      () => {
        // Skip during initial data load to prevent auto-save on page load
        if (this.isInitialDataLoad) {
          console.log('⏭️ Skipping auto-save - initial data load in progress')
          return
        }

        // Schedule database sync (with 3s debounce)
        this.scheduleAutoSave()

        // Note: We DON'T save snapshots here automatically
        // Snapshots are ONLY saved AFTER successful database sync in syncToDatabase()
        // This ensures accurate change detection using the actual payload sent to the backend
      },
      { deep: true }
    )
    
    // Start periodic sync check (every 2 minutes)
    // This ensures data is synced even if user doesn't make changes
    this.startPeriodicSync()

    // Update current time every 30 seconds for real-time sync calculations
    this.timeUpdateInterval = setInterval(() => {
      this.currentTime = Date.now()
    }, 30000) // 30 seconds

    // Initialize multi-tab synchronization listener
    this.coverLetterStore.initStorageListener()

    // Start version polling for cross-browser synchronization
    this.startVersionPolling()

    // Add keyboard shortcuts
    window.addEventListener('keydown', this.handleDebugShortcut)
    window.addEventListener('keydown', this.handleHistoryShortcuts)
    
   
  },
  
  beforeRouteLeave(to, from, next) {
    // Clear timers when navigating away via router
    console.log('🔀 Navigating away from cover letter editor')
    this.cleanupTimers()
    next()
  },
  
  beforeUnmount() {
    console.log('🔴 Component unmounting - cleaning up timers and resources')
    this.cleanupTimers()

    // Destroy multi-tab synchronization listener
    this.coverLetterStore.destroyStorageListener()

    // Remove keyboard shortcut listeners
    window.removeEventListener('keydown', this.handleDebugShortcut)
    window.removeEventListener('keydown', this.handleHistoryShortcuts)
    // Remove global debug function
    delete window.clearCoverLetterData

    console.log('🔴 Component cleanup complete')
  },

  methods: {
    async openPreviewModal(): Promise<void> {
      try {
        console.log('=' .repeat(80))
        console.log('🎯 [edit.vue] openPreviewModal called')
        console.log('=' .repeat(80))

        // Simply open the modal - it will handle its own token and data loading
        // The modal uses the coverLetterToken prop which is already set in this component
        console.log('📝 Opening preview modal with token:', this.coverLetterToken)

        // The modal manages its own standalone token and loads data
        this.showPreviewModal = true
        console.log('✅ Modal opened with showPreviewModal:', this.showPreviewModal)

      } catch (error) {
        console.error('❌ Error in openPreviewModal:', error)
        // @ts-ignore - toast plugin
        this.$toast.error(`Failed to open preview: ${(error as Error).message || 'Unknown error'}`)
      }
    },

    // Centralized cleanup method
    cleanupTimers(): void {
      // Clear all timers to prevent zombie syncs
      if (this.autoSaveTimer) {
        clearTimeout(this.autoSaveTimer)
        this.autoSaveTimer = null
      }
      if (this.periodicSyncTimer) {
        clearInterval(this.periodicSyncTimer)
        this.periodicSyncTimer = null
      }
      if (this.timeUpdateInterval) {
        clearInterval(this.timeUpdateInterval)
        this.timeUpdateInterval = null
      }
      if (this.countdownInterval) {
        clearInterval(this.countdownInterval)
        this.countdownInterval = null
      }
      if (this.versionPollingTimer) {
        clearInterval(this.versionPollingTimer)
        this.versionPollingTimer = null
      }

      // Mark component as unmounted (prevents any queued operations)
      this.isComponentActive = false

      // Clear the cover letter token to prevent any late-firing syncs
      this.coverLetterToken = null
    },

    // Check if user can access premium feature (Attach Resume)
    checkAttachResumeAccess(): void {
      if (!this.isPremiumUser) {
        this.showUpgradeModal = true
        this.showMobileActionsMenu = false
        return
      }
      // TODO: Implement attach resume functionality
      this.showMobileActionsMenu = false
    },

    // Check if user can access premium feature (AI Customize for Job)
    checkAICustomizeAccess(): void {
   

      if (!this.isPremiumUser) {
        this.showUpgradeModal = true
        this.showMobileActionsMenu = false
        return
      }

      this.showJobCustomizeModal = true
      this.showMobileActionsMenu = false
    },

    // Handle timezone calculation when tooltip shows
    async handleTimezoneTooltipShow(): Promise<void> {
      this.isCalculatingTimezone = true

      // Force update of current time to recalculate sync time immediately
      this.currentTime = Date.now()

      // PERFORMANCE FIX: No artificial delay needed - calculation is instant
      // Removed 150ms setTimeout

      this.isCalculatingTimezone = false
    },

    // Handle job customization completed
    handleJobCustomized({ parsedJobData, jobLink, jobDescription }: any): void {
      console.log('Job customization completed:', {
        parsedJobData,
        jobLink,
        jobDescription
      })

      // TODO: Implement actual cover letter customization logic
      // Use parsedJobData to update the cover letter content
      // Example:
      // - Update letter opening to reference the job title and company
      // - Highlight relevant skills from parsedJobData.skills
      // - Tailor content to match requirements and responsibilities

      // For now, just log the data
      console.log('Skills to highlight:', parsedJobData.skills)
      console.log('Requirements to address:', parsedJobData.requirements)
    },
    
    async loadCoverLetterData(): Promise<void> {
      try {
        this.isLoading = true
        this.hasConnectionError = false
        this.coverLetterNotFound = false

        // @ts-expect-error - $axios is injected by plugin
        const { data } = await this.$axios.get(`/cover-letters/${this.coverLetterToken}`)
        
        if (data.coverLetter) {
          const content = JSON.parse(data.coverLetter.content || '{}')

          // Load the title from the database
          this.coverLetterStore.title = data.coverLetter.title || 'My Cover Letter'
          this.previousTitle = this.coverLetterStore.title // Initialize previous title

          // Load the language from the database
          this.coverLetterStore.language = data.coverLetter.language || 'english'

          // Pass token to loadCoverLetter so it knows which cover letter to save to
          this.coverLetterStore.loadCoverLetter(content, this.coverLetterToken)

          // Load sync info (completion percentage and las time) from database
          if (data.coverLetter.completion_percentage !== undefined || data.coverLetter.updated_at) {
            this.coverLetterStore.updateSyncInfo({
              updated_at: data.coverLetter.updated_at,
              completion_percentage: data.coverLetter.completion_percentage || 0
            })

          }

          // Track the initial synced state to enable accurate change detection
          // This prevents the first edit from sending ALL data instead of just changed fields
          this.coverLetterStore.trackSyncedState()
          console.log('✅ Tracked initial synced state - change detection now active')

          // Initialize hash with loaded data to prevent unnecessary initial sync
          this.lastSyncedDataHash = this.computeDataHash(content)
        }
      } catch (error) {
        console.error('Error loading cover letter:', error)
        
      
      } finally {
        this.isLoading = false
      }
    },
    
    retryLoadCoverLetter(): void {
      this.loadCoverLetterData()
    },

    /**
     * Load style settings from database
     */
    async loadStyleSettings(): Promise<void> {
      // Style settings loading has been removed with settingsStore
      console.log('🎨 Style settings loading skipped - functionality removed')
      this.settingsLoaded = true
    },
    
    /**
     * Generate a human-readable description of what changed based on the payload
     * Uses the actual payload sent to backend, not state comparison
     */
    generateChangeDescriptionFromPayload(payload: any): string {
      const changes: string[] = []

      // Check sender info changes
      if (payload.senderInfo && Object.keys(payload.senderInfo).length > 0) {
        const fields = Object.keys(payload.senderInfo).map(key =>
          key.replace(/([A-Z])/g, ' $1').toLowerCase()
        )
        changes.push(`Sender: ${fields.join(', ')}`)
      }

      // Check recipient info changes
      if (payload.recipientInfo && Object.keys(payload.recipientInfo).length > 0) {
        const fields = Object.keys(payload.recipientInfo).map(key =>
          key.replace(/([A-Z])/g, ' $1').toLowerCase()
        )
        changes.push(`Recipient: ${fields.join(', ')}`)
      }

      // Check position info changes
      if (payload.positionInfo && Object.keys(payload.positionInfo).length > 0) {
        const fields = Object.keys(payload.positionInfo).map(key =>
          key.replace(/([A-Z])/g, ' $1').toLowerCase()
        )
        changes.push(`Position: ${fields.join(', ')}`)
      }

      // Check letter content changes
      if (payload.letterContent && Object.keys(payload.letterContent).length > 0) {
        const fields = Object.keys(payload.letterContent).map(key => {
          if (key === 'fullLetter') return 'letter content'
          return key.replace(/([A-Z])/g, ' $1').toLowerCase()
        })
        changes.push(`Content: ${fields.join(', ')}`)
      }

      // Check language change
      if (payload.language !== undefined) {
        changes.push(`Language: ${payload.language}`)
      }

      // Return formatted string
      if (changes.length === 0) {
        return ''
      } else if (changes.length === 1) {
        return changes[0]
      } else if (changes.length === 2) {
        return changes.join(' • ')
      } else {
        // For 3+ changes, show first 2 and count
        return `${changes.slice(0, 2).join(' • ')} +${changes.length - 2} more`
      }
    },

    /**
     * Check if a change is significant enough to warrant a version snapshot
     * @param payload The data payload being synced to the database
     * @returns true if the change is significant
     */
    isSignificantChange(payload: any): boolean {
      // Count total fields changed across all sections
      let fieldCount = 0

      if (payload.senderInfo) {
        fieldCount += Object.keys(payload.senderInfo).length
      }
      if (payload.recipientInfo) {
        fieldCount += Object.keys(payload.recipientInfo).length
      }
      if (payload.positionInfo) {
        fieldCount += Object.keys(payload.positionInfo).length
      }
      if (payload.letterContent) {
        fieldCount += Object.keys(payload.letterContent).length
      }

      // Letter content changes are always significant
      const hasLetterContentChange = payload.letterContent?.fullLetter !== undefined

      // 3+ fields changed is significant (e.g., filling out an entire form section)
      const hasMultipleFieldChanges = fieldCount >= 3

      // Language change is significant
      const hasLanguageChange = payload.language !== undefined

      console.log('🔍 Significance check:', {
        fieldCount,
        hasLetterContentChange,
        hasMultipleFieldChanges,
        hasLanguageChange,
        isSignificant: hasLetterContentChange || hasMultipleFieldChanges || hasLanguageChange
      })

      return hasLetterContentChange || hasMultipleFieldChanges || hasLanguageChange
    },

    scheduleAutoSave(): void {
      // CRITICAL: Check if there are actually any changes before scheduling
      const changedData = this.coverLetterStore.getChangedFieldsPayload()
      if (!changedData) {
        console.log('⏭️ No actual changes detected - skipping auto-save schedule')
        return
      }

      // Mark that we have pending changes to save
      this.hasPendingChanges = true

      const isFirstChange = !this.autoSaveTimer

      // Clear existing timer and countdown (resets the timer on each change)
      if (this.autoSaveTimer) {
        clearTimeout(this.autoSaveTimer)
        this.autoSaveTimer = null
      }

      if (this.countdownInterval) {
        clearInterval(this.countdownInterval)
        this.countdownInterval = null
      }

      // Reset countdown to 2000ms (2 seconds)
      this.saveCountdown = 2000

      // Only log on first change, not every keystroke
      if (isFirstChange) {
        console.log('⏱️ Auto-save scheduled - will save 2 seconds after last change')
      }

      // Update countdown every 100ms for smooth animation
      this.countdownInterval = setInterval(() => {
        this.saveCountdown -= 100
        if (this.saveCountdown <= 0) {
          this.saveCountdown = 0
          if (this.countdownInterval) {
            clearInterval(this.countdownInterval)
            this.countdownInterval = null
          }
        }
      }, 100)

      // Debounce: Wait 2 seconds after last change before saving to API
      // This prevents too many database writes while typing
      this.autoSaveTimer = setTimeout((): void => {
        console.log('💾 Saving to database...')
        this.syncToDatabase()
      }, 2000)
    },
    
    async syncToDatabase(forceSync: boolean = false): Promise<void> {
      if (this.isSaving) return
      
      // 🛡️ SAFETY CHECK 1: Component must still be active (not unmounted)
      if (!this.isComponentActive) {
        console.error('🚨 SYNC ABORTED: Component is no longer active/mounted!')
        return
      }
      
      // 🛡️ SAFETY CHECK 2: Verify we're syncing the correct cover letter
      if (this.coverLetterToken !== this.coverLetterStore.currentToken) {
        console.error('🚨 SYNC ABORTED: Token mismatch!')
        console.error('Page token:', this.coverLetterToken?.substring(0, 10))
        console.error('Store token:', this.coverLetterStore.currentToken?.substring(0, 10))
        console.error('This prevents syncing data from the wrong cover letter.')
        return
      }
      
      // 🛡️ SAFETY CHECK 3: Ensure we have a valid token
      if (!this.coverLetterToken) {
        console.error('🚨 SYNC ABORTED: No cover letter token!')
        return
      }
      
      try {
        this.isSaving = true

        // Get ONLY the fields that changed (partial update for efficiency)
        const changedData = this.coverLetterStore.getChangedFieldsPayload()

        // ⚡ CHANGE DETECTION: Only sync if data actually changed (unless forced)
        if (!forceSync && !changedData) {
          console.log('⏭️ No changes detected - skipping database sync')
          this.isSaving = false
          return
        }

        // Determine what data to send
        let coverLetterData: any
        if (forceSync) {
          console.log('🔥 FORCE SYNC - bypassing change detection')
          // For force sync, send everything
          coverLetterData = {
            senderInfo: this.coverLetterStore.senderInfo,
            recipientInfo: this.coverLetterStore.recipientInfo,
            positionInfo: this.coverLetterStore.positionInfo,
            letterContent: this.coverLetterStore.letterContent,
            language: this.coverLetterStore.language
          }
        } else {
          // For normal sync, send only changed fields
          coverLetterData = changedData
        }
        
        // Detailed logging
        const timestamp = new Date().toLocaleTimeString()
        console.group(`🔄 DATABASE SYNC - ${timestamp}`)
        console.log('📋 Cover Letter Token:', this.coverLetterToken.substring(0, 10) + '...')
        console.log('📝 Cover Letter Title:', this.coverLetterStore.title || '(Untitled)')
        console.log('🎯 Sync Mode:', forceSync ? '🔥 FORCE (full data)' : '⚡ PARTIAL (only changes)')
        console.log('📦 PAYLOAD STRUCTURE (fields being sent):')
        if (coverLetterData.senderInfo) {
          console.log('  ├─ senderInfo:', Object.keys(coverLetterData.senderInfo))
        }
        if (coverLetterData.recipientInfo) {
          console.log('  ├─ recipientInfo:', Object.keys(coverLetterData.recipientInfo))
        }
        if (coverLetterData.positionInfo) {
          console.log('  ├─ positionInfo:', Object.keys(coverLetterData.positionInfo))
        }
        if (coverLetterData.letterContent) {
          console.log('  ├─ letterContent:', Object.keys(coverLetterData.letterContent))
        }
        if (coverLetterData.language !== undefined) {
          console.log('  └─ language:', coverLetterData.language)
        }
        console.log('📦 Full payload data:', coverLetterData)
        console.log('⏱️ Frequency: Saves 1 second after last change (debounced)')
        
        // Save entire cover letter data to database via API
        // @ts-expect-error - $axios is injected by plugin
        const response = await this.$axios.patch(`/cover-letters/${this.coverLetterToken}/sync`, {
          title: this.coverLetterStore.title,
          content: coverLetterData
        })

        console.log('✅ SYNC SUCCESS')
        console.log('📈 Completion:', response.data.completion_percentage + '%')
        console.log('🕐 Server Updated:', response.data.updated_at)
        console.groupEnd()

        // Update sync info in store (completion percentage and last sync time)
        this.coverLetterStore.updateSyncInfo({
          updated_at: response.data.updated_at,
          completion_percentage: response.data.completion_percentage
        })

        // Update server version tracker for cross-browser sync
        this.serverVersion = response.data.updated_at

        // Track the synced state for accurate change detection
        // This ensures detectChanges() and getChangedFieldsPayload() compare against what was actually sent to backend
        this.coverLetterStore.trackSyncedState()

        // Store the payload for later snapshot description generation
        this.lastSyncedPayload = coverLetterData

        // ==========================================
        // SNAPSHOT CREATION ON EVERY DATABASE SAVE
        // ==========================================
        // Save snapshot AFTER every successful database sync
        // This ensures complete history tracking matching database state
        const changeDescription = this.generateChangeDescriptionFromPayload(coverLetterData)

        console.log('📸 Snapshot decision:', {
          changeDescription,
          willSave: !!changeDescription
        })

        if (changeDescription) {
          console.log('✅ Creating snapshot:', changeDescription)
          this.coverLetterStore.saveSnapshot(changeDescription)
          this.lastSnapshotTime = Date.now() // Update timestamp for reference
          console.log('📸 Snapshot saved successfully')
        } else {
          console.log('⏭️ No description generated - skipping snapshot')
        }
      } catch (error) {
        console.groupEnd()
        console.group('❌ SYNC FAILED')
        const err = error as any
        console.error('Error:', err.message)
        console.error('Response:', err.response?.data)
        console.groupEnd()
        // @ts-expect-error - $notify is injected by plugin
        this.$notify?.error('Error', 'Failed to save changes to server')
      } finally {
        setTimeout(() => {
          this.isSaving = false
          this.hasPendingChanges = false
        }, 500)
      }
    },
    
    // Legacy method - kept for backward compatibility
    async saveCurrentStep(): Promise<void> {
      // Redirect to new sync method
      await this.syncToDatabase()
    },

    startPeriodicSync(): void {
      // Sync to database every 2 minutes
      // This ensures data is backed up even if user is idle
      this.periodicSyncTimer = setInterval((): void => {
        console.log('⏰ Periodic sync check (every 2 minutes)')

        // Only sync if store has been modified (has lastSaved timestamp)
        if (this.coverLetterStore.lastSaved) {
          console.log('📤 Triggering periodic sync...')
          this.syncToDatabase()
        } else {
          console.log('⏭️ No changes detected, skipping sync')
        }
      }, 2 * 60 * 1000) // 2 minutes
    },

    // === CROSS-BROWSER VERSION POLLING ===

    /**
     * Start polling database for version changes (cross-browser sync)
     * Checks every 30 seconds if the cover letter was modified in another browser/device
     */
    startVersionPolling(): void {
      console.log('🌐 Starting cross-browser version polling (every 30 seconds)')

      // Check version every 30 seconds
      this.versionPollingTimer = setInterval(async (): Promise<void> => {
        if (!this.isComponentActive || !this.coverLetterToken) {
          return // Component unmounted or no token
        }

        await this.checkServerVersion()
      }, 30000) // 30 seconds
    },

    /**
     * Check if server version is newer than our local version
     */
    async checkServerVersion(): Promise<void> {
      // Prevent concurrent version checks
      if (this.isCheckingVersion) {
        console.log('⏭️ Version check already in progress, skipping')
        return
      }

      this.isCheckingVersion = true

      try {
        // Fetch latest cover letter metadata from server
        // @ts-ignore - axios plugin
        const { data } = await this.$axios.get(`/cover-letters/${this.coverLetterToken}`)

        const serverUpdatedAt = data.coverLetter.updated_at

        // First time - just store the version
        if (!this.serverVersion) {
          this.serverVersion = serverUpdatedAt
          console.log('📌 Stored initial server version:', serverUpdatedAt)
          this.isCheckingVersion = false
          return
        }

        // Check if server version is newer
        if (serverUpdatedAt > this.serverVersion) {
          console.warn('🌐 Cover letter was modified in another browser/device!', {
            currentVersion: this.serverVersion,
            serverVersion: serverUpdatedAt
          })

          // Show notification with action buttons
          this.showVersionConflictNotification(serverUpdatedAt)
        } else {
          console.log('✅ Server version matches local version')
        }
      } catch (error) {
        console.error('❌ Version check error:', error)
      } finally {
        this.isCheckingVersion = false
      }
    },

    /**
     * Show notification when cover letter was modified elsewhere
     */
    showVersionConflictNotification(newServerVersion: string): void {
      // @ts-expect-error - $notify is injected by plugin
      this.$notify?.({
        type: 'warning',
        title: 'Cover Letter Updated Elsewhere',
        text: 'This cover letter was modified in another browser or device. Reload to see the latest version?',
        duration: 0, // Don't auto-dismiss
        actions: [
          {
            label: 'Reload',
            onClick: () => this.reloadFromServer(newServerVersion)
          },
          {
            label: 'Keep Mine',
            onClick: () => this.keepLocalVersion(newServerVersion)
          }
        ]
      })
    },

    /**
     * Reload cover letter data from server (discards local changes)
     */
    async reloadFromServer(newServerVersion: string): Promise<void> {
      console.log('🔄 Reloading cover letter from server...')

      try {
        // Fetch fresh data from server
        await this.loadCoverLetterData()

        // Update our version tracker
        this.serverVersion = newServerVersion

        // @ts-expect-error - $notify is injected by plugin
        this.$notify?.success('Cover Letter Reloaded', 'Latest version loaded successfully')

        console.log('✅ Cover letter reloaded from server')
      } catch (error) {
        console.error('❌ Failed to reload from server:', error)
        // @ts-expect-error - $notify is injected by plugin
        this.$notify?.error('Reload Failed', 'Could not load latest version')
      }
    },

    /**
     * Keep local version and update server version tracker
     * This prevents further notifications until next server change
     */
    keepLocalVersion(newServerVersion: string): void {
      console.log('💾 User chose to keep local version')

      // Update version tracker to suppress notifications
      this.serverVersion = newServerVersion

      // Trigger immediate sync to overwrite server with local changes
      console.log('📤 Syncing local version to server...')
      this.syncToDatabase()

      // @ts-expect-error - $notify is injected by plugin
      this.$notify?.info('Keeping Local Version', 'Your changes will be synced to server')
    },

    computeDataHash(data: any): string {
      // Simple hash function to detect changes
      // Converts data to JSON string and creates a hash
      const str: string = JSON.stringify(data)
      let hash: number = 0
      for (let i = 0; i < str.length; i++) {
        const char: number = str.charCodeAt(i)
        hash = ((hash << 5) - hash) + char
        hash = hash & hash // Convert to 32-bit integer
      }
      return hash.toString()
    },
    
    // Cover letters don't need add/remove item methods
    
    handleDebugShortcut(event: KeyboardEvent): void {
      // Ctrl+Shift+D or Cmd+Shift+D to trigger data comparison
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'D') {
        event.preventDefault()
        console.clear()

        // Fetch fresh data from database and compare
        // @ts-ignore - axios plugin
        this.$axios.get(`/cover-letters/${this.coverLetterToken}`)
          .then(({ data }: any): void => {
            if (data.coverLetter) {
              const content = JSON.parse(data.coverLetter.content || '{}')
              this.logDataComparison(content)
            }
          })
          .catch((error: Error): void => {
            console.error('Failed to fetch database data:', error)
          })
      }
    },

    handleHistoryShortcuts(event: KeyboardEvent): void {
      // Ctrl+Z or Cmd+Z to undo
      if ((event.ctrlKey || event.metaKey) && event.key === 'z' && !event.shiftKey) {
        event.preventDefault()
        const success = this.coverLetterStore.undo()
        if (success) {
          // @ts-ignore - notify plugin
          this.$notify.success('Undo', 'Reverted to previous version')
        } else {
          // @ts-ignore - notify plugin
          this.$notify.info('Undo', 'No more history to undo')
        }
      }

      // Ctrl+Y or Cmd+Shift+Z to redo
      if (
        ((event.ctrlKey || event.metaKey) && event.key === 'y') ||
        ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'z')
      ) {
        event.preventDefault()
        const success = this.coverLetterStore.redo()
        if (success) {
          // @ts-ignore - notify plugin
          this.$notify.success('Redo', 'Restored to next version')
        } else {
          // @ts-ignore - notify plugin
          this.$notify.info('Redo', 'No more history to redo')
        }
      }

      // Ctrl+H or Cmd+H to show history modal
      if ((event.ctrlKey || event.metaKey) && event.key === 'h') {
        event.preventDefault()
        this.showHistoryModal = true
      }

      // Ctrl+S or Cmd+S to manually save snapshot
      if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault()
        // Use last synced payload to generate accurate description
        if (this.lastSyncedPayload) {
          const description = this.generateChangeDescriptionFromPayload(this.lastSyncedPayload)
          this.coverLetterStore.saveSnapshot(description || 'Manual save')
          this.lastSnapshotTime = Date.now() // Reset 5-minute interval timer
        } else {
          this.coverLetterStore.saveSnapshot('Manual save')
          this.lastSnapshotTime = Date.now() // Reset 5-minute interval timer
        }
        // @ts-ignore - notify plugin
        this.$notify.success('Saved', 'Version snapshot created')
      }
    },

    logDataComparison(databaseData: any): void {
      // Get localStorage data
      const storageKey: string = `cover_letter_data_${this.coverLetterToken}`
      const localStorageRaw: string | null = localStorage.getItem(storageKey)
      const localStorageData: any = localStorageRaw ? JSON.parse(localStorageRaw) : null
      
      console.group('📊 DATA COMPARISON: localStorage vs Database')
      console.log('🔑 Cover Letter Token:', this.coverLetterToken.substring(0, 15) + '...')
      console.log('📍 Storage Key:', storageKey)
      console.log('')
      
     
      
      if (localStorageData && databaseData) {
        console.log('🔍 DETAILED COMPARISON:')
        console.log('')
        
        // Compare specific fields
        const fields = [
          { key: 'senderInfo', label: 'Sender Info' },
          { key: 'recipientInfo', label: 'Recipient Info' },
          { key: 'positionInfo', label: 'Position Info' },
          { key: 'letterContent', label: 'Letter Content' }
        ]
        
        const fieldComparison = {}
        fields.forEach(field => {
          const localValue = localStorageData[field.key]
          const dbValue = databaseData[field.key]
          
          let status = '❓'
          if (JSON.stringify(localValue) === JSON.stringify(dbValue)) {
            status = '✅ Synced'
          } else {
            status = '⚠️ Different'
          }
          
          // Get counts for arrays
          const localCount = Array.isArray(localValue) ? localValue.length : (localValue ? 1 : 0)
          const dbCount = Array.isArray(dbValue) ? dbValue.length : (dbValue ? 1 : 0)
          
          fieldComparison[field.label] = `${status} (Local: ${localCount}, DB: ${dbCount})`
        })
        
        console.table(fieldComparison)
      }
      
      // Log full data for inspection
      console.log('📦 localStorage Data:', localStorageData)
      console.log('🗄️ Database Data:', databaseData)
      
      // Calculate hashes (only compare content fields, not metadata)
      if (localStorageData && databaseData) {
        // Extract only content fields for fair comparison
        const extractContent = (data) => ({
          senderInfo: data.senderInfo,
          recipientInfo: data.recipientInfo,
          positionInfo: data.positionInfo,
          letterContent: data.letterContent
        })
        
        const localContent = extractContent(localStorageData)
        const dbContent = extractContent(databaseData)
        
        const localHash = this.computeDataHash(localContent)
        const dbHash = this.computeDataHash(dbContent)
        console.log('')
        console.log('🔐 Content Hashes (excluding metadata):')
        console.log('  localStorage:', localHash)
        console.log('  Database:', dbHash)
        console.log('  Match:', localHash === dbHash ? '✅ Yes' : '❌ No')
        
        if (localHash !== dbHash) {
          console.warn('⚠️ Data out of sync! Consider clearing localStorage or syncing to database.')
        }
      }
      
      console.groupEnd()
    },
    
    async clearAllCoverLetterData(): Promise<void> {
      if (!confirm('⚠️ Are you sure? This will clear ALL data for this cover letter from both localStorage and database!')) {
        return
      }

      console.group('🗑️ CLEARING COVER LETTER DATA')

      try {
        // 1. Clear localStorage
        const storageKey: string = `cover_letter_data_${this.coverLetterToken}`
        localStorage.removeItem(storageKey)
        console.log('✅ Cleared localStorage:', storageKey)

        // 2. Reset store to defaults
        this.coverLetterStore.resetToDefaults()
        console.log('✅ Reset store to defaults')

        // 3. Sync empty data to database
        await this.syncToDatabase()
        console.log('✅ Synced empty data to database')

        // 4. Reload page
        console.log('🔄 Reloading page...')
        console.groupEnd()
        setTimeout((): void => {
          window.location.reload()
        }, 1000)

      } catch (error) {
        console.error('❌ Error clearing data:', error)
        console.groupEnd()
      }
    },

    async saveCoverLetterTitle(): Promise<void> {
      // Only save if the title actually changed
      if (this.coverLetterStore.title === this.previousTitle) {
        console.log('⏭️ Title unchanged, skipping save')
        return
      }

      console.log('💾 Saving cover letter title immediately:', this.coverLetterStore.title)

      // Save to localStorage first
      this.coverLetterStore.saveCoverLetter()

      // Immediately sync to database with force flag (bypasses change detection)
      await this.syncToDatabase(true)

      // Update previous title
      this.previousTitle = this.coverLetterStore.title

      // @ts-ignore - notify plugin
      this.$notify.success('Cover Letter Title Updated', `Your cover letter is now called "${this.coverLetterStore.title}"`, 3000)
    },

    scrollSidebarDown(): void {
      const sidebarNav = this.$refs.sidebarNav as HTMLElement | undefined
      if (sidebarNav) {
        sidebarNav.scrollBy({
          top: 200,
          behavior: 'smooth'
        })
      }
    },

    async navigateToStep(stepId: number): Promise<void> {
      // Clear any pending auto-save timers and indicators
      if (this.autoSaveTimer) {
        clearTimeout(this.autoSaveTimer)
        this.autoSaveTimer = null
      }
      if (this.countdownInterval) {
        clearInterval(this.countdownInterval)
        this.countdownInterval = null
      }
      this.hasPendingChanges = false
      this.saveCountdown = 0

      // Save will only happen if there are actual changes
      await this.saveCurrentStep()

      // Change step immediately
      this.step = stepId
    },

    async nextStep(): Promise<void> {
      // Clear any pending auto-save timers and indicators
      if (this.autoSaveTimer) {
        clearTimeout(this.autoSaveTimer)
        this.autoSaveTimer = null
      }
      if (this.countdownInterval) {
        clearInterval(this.countdownInterval)
        this.countdownInterval = null
      }
      this.hasPendingChanges = false
      this.saveCountdown = 0

      // Save will only happen if there are actual changes
      await this.saveCurrentStep()

      // Note: Snapshots are now created ONLY after successful database sync
      // This happens in syncToDatabase() after the API call completes
      // No snapshots are created during step navigation to avoid premature/inaccurate snapshots

      if (this.step === this.finalStep) {
        // Stay on preview page - user can download from there
        // @ts-ignore - toast plugin
        this.$toast.success('Cover letter completed! You can now download it.')
        // Note: Final snapshot will be created after the last database sync
        // No need to create a manual "Cover letter completed" snapshot here
      } else {
        this.step++
      }
    },

    goToTemplateSelection(): void {
      // Find template selection step ID
      const templateStep = this.wizardSteps.find((s: WizardStep) => s.component === 'TemplateSelection')
      if (templateStep) {
        this.step = templateStep.id
      }
    },

    async handleDownloadPDF(data: any): Promise<void> {
      // @ts-ignore - toast plugin
      this.$toast.info('PDF download functionality coming soon!')
      console.log('Download PDF:', data)
    },

    async handleDownloadDOCX(data: any): Promise<void> {
      // @ts-ignore - toast plugin
      this.$toast.info('DOCX download functionality coming soon!')
      console.log('Download DOCX:', data)
    },

    // Handle job customization next button
    async handleJobCustomizeNext(): Promise<void> {
      // Close first modal
      this.showJobCustomizeModal = false
      // TODO: Implement parsing modal logic
    },

    // Handle template selection
    selectTemplate(templateSlug: string): void {
      console.log('🎨 User selected template:', templateSlug)
      this.selectedTemplate = templateSlug
      // The watcher will handle updating the store
    },

    openCustomizeWithFreeFilter(): void {
      // TODO: Implement free template filter
      console.log('Opening template selection with free filter')
    },

    async previousStep(): Promise<void> {
      // Simply go back one step (no saving needed)
      if (this.step > 3) {
        this.step--
      }
    }
  }
}
</script>

<style scoped lang="scss">
.page-with-bg {
  position: relative;
  background-size: cover;
  background-position: center top;
  background-repeat: no-repeat;
  background-attachment: fixed;
}

.page-with-bg>* {
  position: relative;
  z-index: 1;
}

.wizard-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  height: 85vh;
  transition: height 0.3s ease;
  overflow: visible;
  border-radius: 0.5rem;

  &:has(.sidebar-expanded) {
    height: 90vh;
  }
}

.wizard-sidebar {
  position: sticky;
  top: 0;
  height: 85vh;
  overflow: hidden;
  transition: height 0.3s ease;
  display: flex;
  flex-direction: column;
  border-top-left-radius: 0.5rem;
  border-bottom-left-radius: 0.5rem;

  &.sidebar-expanded {
    height: 90vh;
  }
}

.expand-toggle {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
}

.cover-letter-title-input,
.resume-title-input {
  width: 100%;
  padding: 0.25rem 0;
  cursor: text;
  border-bottom: 1px solid transparent;
  
  &:hover {
    border-bottom-color: rgba(255, 255, 255, 0.2);
  }
  
  &:focus {
    cursor: text;
    border-bottom-color: rgba(255, 255, 255, 0.4);
  }
  
  &::placeholder {
    opacity: 0.6;
  }
}

.sync-tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  min-width: 200px;
}

.sync-tooltip-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  font-size: 0.75rem;
}

.sync-tooltip-label {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  white-space: nowrap;
}

.sync-tooltip-value {
  color: white;
  font-weight: 600;
  text-align: right;
}

.sidebar-nav-scrollable {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.sidebar-nav-scrollable::-webkit-scrollbar {
  display: none;
}

.wizard-content {
  height: 85vh;
  overflow: visible;
  display: flex;
  flex-direction: column;
  background-color: white;
  border-top-right-radius: 0.5rem;
  border-bottom-right-radius: 0.5rem;
}

.wizard-layout:has(.sidebar-expanded) .wizard-content {
  height: 90vh;
}

.wizard-step-content-animated {
  flex: 1;
  overflow-y: auto;
  overflow-x: visible;
}

.wizard-step-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: visible;
  padding: 2rem;
}

.feature-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-500);
  
  svg {
    width: 24px;
    height: 24px;
  }
}

.wizard-step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  flex-shrink: 0;
  position: relative;
  z-index: 10;
  background-color: white;
}

.save-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 11;

  .cursor-pointer:hover {
    opacity: 0.8;
    transition: opacity 0.2s ease;
  }

  // Override tooltip z-index for sync status
  :deep(.hb-tooltip) {
    z-index: 150 !important;
  }

  // Ensure tooltip container doesn't clip
  :deep(.hb-tooltip-container) {
    position: relative;
    z-index: 11;
  }
}

.wizard-step-footer {
  display: flex;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  border-top: 1px solid var(--gray-200);
  background-color: white;
  flex-shrink: 0;
  width: 100%;
  box-sizing: border-box;
}

.sidebar-step {
  cursor: pointer;
  transition: all 0.2s ease;

  &:not(.sidebar-step--ellipsis):hover .flex {
    background-color: rgba(255, 255, 255, 0.05);
  }
}

.sidebar-step--active .flex {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-step--completed .step-number {
  background-color: #32BEA6;
  color: white;
}

.sidebar-step--active .step-number {
  background-color: var(--primary-500);
  color: white;
}

.sidebar-step--upcoming .step-number {
  background-color: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.9);
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.step-info {
  flex: 1;
}

.step-title {
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.125rem;
}

.step-subtitle {
  font-size: 0.75rem;
  opacity: 0.7;
}

.sidebar-step--upcoming .step-title,
.sidebar-step--upcoming .step-subtitle {
  opacity: 0.8;
}

.additional-section-card {
  transition: transform 0.2s ease;
}

.additional-section-card:hover {
  transform: translateY(-2px);
}

.skeleton-box {
  background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }

  100% {
    background-position: -200% 0;
  }
}

/* Professional Summary Layout with Suggestions */
.professional-summary-layout {
  display: flex;
  gap: 1.5rem;
  width: 100%;
}

.summary-editor-section {
  flex: 0 0 65%;
  min-width: 0;
}

.summary-suggestions-section {
  flex: 0 0 35%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 600px;
}

.suggestions-header {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.suggestions-title {
  font-weight: 600;
  color: var(--primary-500);
  text-transform: uppercase;
  font-size: 14px;
  letter-spacing: 1px;
  margin: 0;
}

.suggestions-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-right: 0.5rem;
}

/* Custom scrollbar for suggestions */
.suggestions-list::-webkit-scrollbar {
  width: 6px;
}

.suggestions-list::-webkit-scrollbar-track {
  background: var(--gray-100);
  border-radius: 3px;
}

.suggestions-list::-webkit-scrollbar-thumb {
  background: var(--gray-300);
  border-radius: 3px;
}

.suggestions-list::-webkit-scrollbar-thumb:hover {
  background: var(--gray-400);
}

.suggestion-card {
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-card:hover {
  border-color: var(--primary-500) !important;
  background: var(--primary-50);
}

.suggestion-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--gray-900);
  margin: 0 0 0.5rem 0;
}

.suggestion-preview {
  font-size: 0.75rem;
  color: var(--gray-600);
  line-height: 1.4;
  margin: 0 0 0.5rem 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.suggestion-category {
  display: inline-block;
  font-size: 0.625rem;
  font-weight: 500;
  color: var(--primary-700);
  background: var(--primary-100);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.no-results {
  padding: 2rem 1rem;
  text-align: center;
  color: var(--gray-500);
  font-size: 0.875rem;
}

/* Responsive adjustments for suggestions panel */
@media (max-width: 1024px) {
  .professional-summary-layout {
    flex-direction: column;
  }
  
  .summary-editor-section,
  .summary-suggestions-section {
    flex: 1 1 auto;
    max-height: none;
  }
  
  .summary-suggestions-section {
    max-height: 400px;
  }
}

/* ============================================
   MOBILE HORIZONTAL STEPS (Default hidden)
   ============================================ */
.mobile-steps-header {
  display: none; /* Hidden on desktop */
}

.mobile-actions-button {
  display: none; /* Hidden on desktop */
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  padding: 0.25rem;
  cursor: pointer;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
  
  &:active {
    background-color: rgba(255, 255, 255, 0.2);
  }
}

.mobile-actions-menu {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 150;
}

.mobile-actions-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  animation: fadeIn 0.2s ease;
}

.mobile-actions-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-radius: 1rem 1rem 0 0;
  max-height: 80vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.mobile-actions-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--gray-200);
  position: sticky;
  top: 0;
  background: white;
  z-index: 1;
}

.mobile-actions-close {
  background: none;
  border: none;
  color: var(--gray-600);
  font-size: 1.5rem;
  padding: 0.25rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  
  &:hover {
    background-color: var(--gray-100);
  }
}

.mobile-actions-list {
  padding: 0.5rem 0;
}

.mobile-action-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: none;
  border: none;
  text-align: left;
  font-size: 1rem;
  color: var(--gray-900);
  cursor: pointer;
  transition: background-color 0.2s ease;
  
  i {
    font-size: 1.25rem;
    width: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  span {
    flex: 1;
  }
  
  &:hover {
    background-color: var(--gray-50);
  }
  
  &:active {
    background-color: var(--gray-100);
  }
  
  &--primary {
    background-color: var(--primary-50);
    color: var(--primary-700);
    font-weight: 600;
    
    i {
      color: var(--primary-600);
    }
    
    &:hover {
      background-color: var(--primary-100);
    }
  }
}

.mobile-action-status {
  padding: 1rem 1.25rem;
  background: var(--gray-50);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  border-top: 2px solid var(--gray-200);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

/* ============================================
   RESPONSIVE STYLES
   ============================================ */

/* Tablet (641px - 1024px) */
@media (max-width: 1024px) and (min-width: 641px) {
  .page-with-bg {
    padding: 1rem;
  }

  .container {
    padding: 0 1rem;
  }

  /* Wizard Layout - Reduce sidebar width */
  .wizard-layout {
    grid-template-columns: 280px 1fr;
  }

  .wizard-sidebar .p-6 {
    padding: 1.25rem;
  }

  /* Compact step items */
  .sidebar-nav-item {
    padding: 0.75rem;
  }

  .step-number {
    width: 32px;
    height: 32px;
    font-size: 0.813rem;
  }

  .step-title {
    font-size: 0.875rem;
  }

  .step-subtitle {
    font-size: 0.75rem;
  }

  /* Wizard content adjustments */
  .wizard-step-content {
    padding: 1.5rem;
  }

  .wizard-step-header {
    padding: 1rem 1.5rem;
    gap: 0.75rem;
  }

  .wizard-step-footer {
    padding: 1rem 1.5rem;
  }

  /* Compact header buttons on tablet */
  .wizard-step-header {
    :deep(button) {
      span {
        font-size: 0.813rem;
      }
    }
  }

  /* Hide mobile horizontal steps on tablet */
  .mobile-steps-header {
    display: none;
  }
  
  /* Form adjustments for tablet */
  .form-row {
    gap: 1rem;
  }
  
  /* Professional summary layout for tablet */
  .professional-summary-layout {
    flex-direction: column;
  }
  
  .summary-editor-section,
  .summary-suggestions-section {
    max-height: 400px;
  }
}

/* Mobile phones (≤640px) */
@media (max-width: 640px) {
  .page-with-bg {
    padding: 0;
    min-height: 100vh;
  }

  .container {
    padding: 0;
    max-width: 100%;
  }
  
  .card-container-shadow {
    box-shadow: none;
    border-radius: 0;
  }

  /* Show mobile horizontal steps */
  .mobile-steps-header {
    display: block;
    background: var(--primary-700);
    border-radius: 0;
    overflow: hidden;
  }

  .mobile-steps-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 1rem 1rem 0;
    
    h2 {
      flex: 1;
      min-width: 0;
      margin: 0;
    }
  }
  
  .mobile-actions-button {
    display: flex; /* Show on mobile */
  }

  .mobile-steps-scroll {
    overflow-x: auto;
    overflow-y: hidden;
    scrollbar-width: none;
    -ms-overflow-style: none;
    
    &::-webkit-scrollbar {
      display: none;
    }
  }

  .mobile-steps-container {
    display: flex;
    gap: 0.5rem;
    padding: 1rem;
    min-width: min-content;
  }

  .mobile-step-item {
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.375rem;
    padding: 0.5rem 0.75rem;
    background: rgba(255, 255, 255, 0.15);
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    min-width: 80px;
    
    &--active {
      background: white;
      
      .mobile-step-icon {
        background: var(--primary-700);
        color: white;
      }
      
      .mobile-step-label {
        color: var(--primary-700);
        font-weight: 600;
      }
    }
    
    &--completed {
      .mobile-step-icon {
        background: #32BEA6;
        color: white;
      }
      
      .mobile-step-label {
        color: rgba(255, 255, 255, 0.9);
      }
    }
    
    &--upcoming {
      background: rgba(255, 255, 255, 0.1);
      
      .mobile-step-label {
        color: rgba(255, 255, 255, 0.5);
      }
    }
    
    &--more {
      background: transparent;
      color: rgba(255, 255, 255, 0.5);
      cursor: default;
      min-width: 60px;
    }
    
    &:active:not(.mobile-step-item--more) {
      transform: scale(0.95);
    }
  }

  .mobile-step-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.875rem;
    background: rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.9);
  }

  .mobile-step-number {
    display: block;
  }

  .mobile-step-check {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.125rem;
  }
  
  .mobile-step-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.9);
    white-space: nowrap;
    text-align: center;
    line-height: 1.2;
  }

  /* Hide desktop sidebar completely */
  .wizard-sidebar {
    display: none !important;
  }

  /* Wizard Layout - Single column for mobile */
  .wizard-layout {
    grid-template-columns: 1fr;
    height: calc(100vh - 2.25rem);
    min-height: calc(100vh - 2.25rem);
    max-height: calc(100vh - 2.25rem);
    margin-top: 2.25rem;
    border-radius: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  /* Content Area - Take remaining space */
  .wizard-content {
    flex: 1;
    height: auto;
    min-height: 0;
    border-radius: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .wizard-step-header {
    display: none; /* Hide on mobile - actions shown in horizontal steps */
  }

  .wizard-step-content-animated {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding-bottom: 80px; /* Space for sticky footer */
  }

  .wizard-step-content {
    padding: 1rem;
    min-height: auto;
  }

  /* Sticky Footer Navigation */
  .wizard-step-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 1rem;
    gap: 0.5rem;
    background: white;
    border-top: 1px solid var(--gray-200);
    z-index: 50;
    flex-shrink: 0;
    
    /* Full width buttons */
    :deep(button) {
      flex: 1;
      justify-content: center;
    }
  }

  /* Form layouts - Stack inputs */
  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .form-group {
    width: 100%;
  }

  /* Loading/Error states */
  .bg-white.py-24 {
    padding-top: 3rem;
    padding-bottom: 3rem;
    padding-left: 1rem;
    padding-right: 1rem;
  }

  /* Resume title input */
  .resume-title-input,
  .cover-letter-title-input {
    font-size: 1rem;
  }

  /* Step numbers - smaller on mobile */
  .step-number {
    width: 28px;
    height: 28px;
    font-size: 0.75rem;
  }
}

/* Mobile phones (480px) */
@media (max-width: 480px) {
  .page-with-bg {
    padding: 0.5rem 0;
  }

  .wizard-step-content {
    padding: 0.75rem;
  }

  .wizard-step-header {
    padding: 0.5rem 0.75rem;
  }

  .wizard-step-footer {
    padding: 0.75rem;
  }

  /* Smaller text on very small screens */
  .wizard-step-content h3 {
    font-size: 1.25rem;
  }

  .wizard-step-content p {
    font-size: 0.875rem;
  }

  /* Button adjustments */
  .wizard-step-footer button {
    font-size: 0.875rem;
    padding: 0.5rem 0.75rem;
  }

  /* Tighter form spacing */
  .form-group {
    margin-bottom: 0.75rem;
  }

  /* Save status - stack if needed */
  .save-status {
    font-size: 0.75rem;
  }

  .sidebar-nav-scrollable {
    max-height: 200px;
  }
}

/* Very small phones (≤480px) - Additional adjustments */
@media (max-width: 480px) {
  /* Already handled in 640px breakpoint, this is for extra-small adjustments */

  .wizard-step-content {
    padding: 1.5rem;
  }

  .step-subtitle {
    font-size: 0.688rem;
  }
}

/* Very large screens (1440px+) */
@media (min-width: 1440px) {
  .wizard-layout {
    grid-template-columns: 320px 1fr;
  }

  .wizard-step-content {
    padding: 2.5rem;
    max-width: 1200px;
    margin: 0 auto;
  }
}

/* Print styles */
@media print {
  .wizard-sidebar,
  .wizard-step-header,
  .wizard-step-footer {
    display: none !important;
  }

  .wizard-layout {
    grid-template-columns: 1fr;
  }

  .wizard-content {
    height: auto;
  }

  .wizard-step-content {
    padding: 0;
  }
}

/* Final Preview Layout Styles */
.preview-final-layout {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 2rem;
  padding: 2rem;
  min-height: 600px;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    padding: 1rem;
  }
}

.preview-final-info {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}


.template-characteristics {
  padding: 1rem;
  background: var(--gray-50);
  border-radius: 0.5rem;
}



.preview-final-display {
  position: relative;
  
  .preview-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 600px;
    background: white;
    border-radius: 0.75rem;
    
    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 3px solid var(--primary-200);
      border-top: 3px solid var(--primary-500);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 1rem;
    }
    
    .loading-text {
      color: var(--gray-600);
      font-size: 14px;
      font-weight: 500;
    }
  }
}

.preview-final-document {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--gray-50);
  border-radius: 0.75rem;
  overflow: hidden;
  min-height: 600px;
}

.golden-laurel-bg {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: auto;
  pointer-events: none;
  z-index: 105;
  
  img {
    width: 100%;
    height: auto;
    display: block;
  }
  
  @media (max-width: 768px) {
    width: 400px;
  }
}

.preview-document-container {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  z-index: 1;
}

.preview-document-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  background: white;
  border-bottom: 1px solid var(--gray-200);
}

.preview-document-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preview-page-nav-compact {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.page-nav-btn-compact {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--gray-300);
  border-radius: 0.375rem;
  background: white;
  color: var(--gray-700);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: var(--gray-50);
    border-color: var(--gray-400);
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  i {
    font-size: 1.25rem;
  }
}

.page-info-compact {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--gray-700);
  min-width: 3rem;
  text-align: center;
}

.preview-document-content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  background: var(--gray-100);
  display: flex;
  justify-content: center;
}

.preview-page-wrapper {
  background: white;
}

.preview-page {
  width: 210mm;
  min-height: 297mm;
  background: white;
  padding: 1in;
  
  @media (max-width: 768px) {
    width: 100%;
    min-height: auto;
  }
}

.preview-page-inner {
  width: 100%;
  height: 100%;
}

/* Job Bullet - Rounded Square */
.job-bullet {
  display: inline-block;
  width: 6px;
  height: 6px;
  background-color: var(--primary-500);
  border-radius: 2px;
  margin-top: 6px;
  flex-shrink: 0;
}

// Shimmer animation for "Saving..." text - continuous left to right
@keyframes textShimmer {
  0% {
    background-position: 200% center;
  }
  100% {
    background-position: -200% center;
  }
}

.saving-shimmer-text {
  background: linear-gradient(
    90deg,
    var(--primary-500) 0%,
    var(--primary-300) 50%,
    var(--primary-500) 100%
  );
  background-size: 200% 100%;
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: textShimmer 1.7s linear infinite;
}
</style>

<!-- Non-scoped styles for dynamically injected HTML content -->
<style lang="scss">
/* Keyword Highlight - Must be unscoped for v-html content */
.keyword-highlight {
  padding: 1px 4px;
  background-color: var(--primary-50);
  border: 1px solid var(--primary-400);
  border-radius: 6px;
}
</style>
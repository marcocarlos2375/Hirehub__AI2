// @ts-strict
/**
 * Component Props Type Definitions
 *
 * Centralized type definitions for Vue component props
 */

import type { RouteLocationRaw } from 'vue-router'

// ==================== COMMON TYPES ====================

export type ButtonVariant =
  | 'primary'
  | 'secondary'
  | 'outline'
  | 'ghost'
  | 'dark-ghost'
  | 'danger'
  | 'white'
  | 'light'
  | 'light-gray'
  | 'link'
  | 'transparent'

export type ButtonSize = 'sm' | 'md' | 'lg'
export type ButtonRounded = 'default' | 'pill'
export type ButtonType = 'button' | 'submit' | 'reset'
export type LinkTarget = '_self' | '_blank' | '_parent' | '_top'

export type InputSize = 'sm' | 'md' | 'lg'
export type InputAppearance = 'dark' | 'gray' | 'light' | 'white'
export type InputType =
  | 'text'
  | 'email'
  | 'password'
  | 'number'
  | 'tel'
  | 'url'
  | 'search'
  | 'date'
  | 'textarea'
  | 'birthdate'

export type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | '6xl' | '7xl'
export type ModalAppearance = 'white' | 'light' | 'dark'

export type BadgeVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info' | 'default'
export type BadgeSize = 'xs' | 'sm' | 'md' | 'lg'

export type SpinnerSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl'
export type SpinnerColor = 'primary' | 'secondary' | 'white' | 'gray' | 'danger' | string

// ==================== COMPONENT PROPS ====================

export interface HbButtonProps {
  variant?: ButtonVariant
  size?: ButtonSize
  rounded?: ButtonRounded
  fullWidth?: boolean
  disabled?: boolean
  loading?: boolean
  type?: ButtonType
  to?: string | RouteLocationRaw
  href?: string
  target?: LinkTarget
  download?: boolean | string
  border?: boolean
  iconOnly?: boolean
}

export interface HbInputProps {
  modelValue?: string | number
  id?: string
  label?: string
  size?: InputSize
  appearance?: InputAppearance
  type?: InputType
  placeholder?: string
  required?: boolean
  disabled?: boolean
  error?: string | boolean
  helperText?: string
  autofocus?: boolean
  autocomplete?: string
  pattern?: string
}

export interface HbModalProps {
  modelValue?: boolean
  show?: boolean
  title?: string
  appearance?: ModalAppearance
  size?: ModalSize
  showCloseButton?: boolean
  noPadding?: boolean
  persistent?: boolean
  class?: string | object | any[]
}

export interface HbBadgeProps {
  variant?: BadgeVariant
  size?: BadgeSize
  rounded?: boolean
  outline?: boolean
  removable?: boolean
}

export interface HbSpinnerProps {
  size?: SpinnerSize
  color?: SpinnerColor
}

export interface HbCardProps {
  title?: string
  subtitle?: string
  bordered?: boolean
  hoverable?: boolean
  clickable?: boolean
  padding?: boolean
  appearance?: 'white' | 'light' | 'gray' | 'dark'
}

export interface HbCheckboxProps {
  modelValue?: boolean | any[]
  id?: string
  label?: string
  value?: any
  disabled?: boolean
  required?: boolean
  error?: string | boolean
  size?: 'sm' | 'md' | 'lg'
}

export interface HbRadioProps {
  modelValue?: any
  id?: string
  label?: string
  value: any
  name?: string
  disabled?: boolean
  required?: boolean
  error?: string | boolean
  size?: 'sm' | 'md' | 'lg'
}

export interface HbSelectProps {
  modelValue?: any
  id?: string
  label?: string
  options: Array<{ value: any; label: string; disabled?: boolean }>
  placeholder?: string
  disabled?: boolean
  required?: boolean
  error?: string | boolean
  size?: InputSize
  appearance?: InputAppearance
  multiple?: boolean
  searchable?: boolean
}

export interface HbToggleProps {
  modelValue?: boolean
  id?: string
  label?: string
  disabled?: boolean
  size?: 'sm' | 'md' | 'lg'
  labelPosition?: 'left' | 'right'
}

export interface HbAvatarProps {
  src?: string
  alt?: string
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'
  shape?: 'circle' | 'square'
  fallback?: string
  status?: 'online' | 'offline' | 'away' | 'busy'
}

export interface HbIconProps {
  name: string
  size?: number | string
  color?: string
  stroke?: number
}

export interface HbTooltipProps {
  content?: string
  position?: 'top' | 'right' | 'bottom' | 'left'
  trigger?: 'hover' | 'click' | 'focus'
  disabled?: boolean
}

export interface HbProgressBarProps {
  value: number
  max?: number
  size?: 'sm' | 'md' | 'lg'
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  showLabel?: boolean
  animated?: boolean
}

export interface HbPaginationProps {
  currentPage: number
  totalPages: number
  maxVisibleButtons?: number
  disabled?: boolean
}

export interface HbTabsProps {
  modelValue?: number | string
  tabs: Array<{ id?: string | number; label: string; icon?: string; disabled?: boolean }>
  variant?: 'default' | 'pills' | 'underline'
  size?: 'sm' | 'md' | 'lg'
}

export interface HbTableProps {
  columns: Array<{ key: string; label: string; sortable?: boolean; width?: string }>
  rows: any[]
  loading?: boolean
  striped?: boolean
  hoverable?: boolean
  bordered?: boolean
  compact?: boolean
  selectable?: boolean
  selectedRows?: any[]
}

export interface HbBreadcrumbsProps {
  items: Array<{ label: string; to?: string | RouteLocationRaw; active?: boolean }>
  separator?: string
}

export interface HbStepperProps {
  steps: Array<{ label: string; description?: string; completed?: boolean; active?: boolean }>
  currentStep: number
  orientation?: 'horizontal' | 'vertical'
}

export interface HbRangeProps {
  modelValue: number
  id?: string
  label?: string
  min?: number
  max?: number
  step?: number
  disabled?: boolean
  showValue?: boolean
  unit?: string
}

export interface HbColorPickerProps {
  modelValue?: string
  id?: string
  label?: string
  disabled?: boolean
  format?: 'hex' | 'rgb' | 'hsl'
  presets?: string[]
}

export interface HbDatepickerProps {
  modelValue?: Date | string
  id?: string
  label?: string
  placeholder?: string
  disabled?: boolean
  minDate?: Date | string
  maxDate?: Date | string
  format?: string
  required?: boolean
}

export interface HbFileProps {
  modelValue?: File | File[]
  id?: string
  label?: string
  accept?: string
  multiple?: boolean
  disabled?: boolean
  maxSize?: number
  error?: string | boolean
}

export interface HbWysiwygProps {
  modelValue?: string
  id?: string
  label?: string
  placeholder?: string
  disabled?: boolean
  minHeight?: number
  maxHeight?: number
  toolbar?: string[]
}

// ==================== EMITS ====================

export interface HbButtonEmits {
  (e: 'click', event: MouseEvent): void
}

export interface HbInputEmits {
  (e: 'update:modelValue', value: string | number): void
  (e: 'blur'): void
  (e: 'focus'): void
}

export interface HbModalEmits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
}

export interface HbCheckboxEmits {
  (e: 'update:modelValue', value: boolean | any[]): void
  (e: 'change', value: boolean | any[]): void
}

export interface HbSelectEmits {
  (e: 'update:modelValue', value: any): void
  (e: 'change', value: any): void
}

export interface HbToggleEmits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'change', value: boolean): void
}

export interface HbPaginationEmits {
  (e: 'update:currentPage', page: number): void
  (e: 'page-change', page: number): void
}

export interface HbTabsEmits {
  (e: 'update:modelValue', value: number | string): void
  (e: 'tab-change', value: number | string): void
}

export interface HbRangeEmits {
  (e: 'update:modelValue', value: number): void
  (e: 'change', value: number): void
}

export interface HbColorPickerEmits {
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
}

export interface HbDatepickerEmits {
  (e: 'update:modelValue', value: Date | string): void
  (e: 'change', value: Date | string): void
}

export interface HbFileEmits {
  (e: 'update:modelValue', value: File | File[]): void
  (e: 'change', files: File | File[]): void
}

export interface HbWysiwygEmits {
  (e: 'update:modelValue', value: string): void
}

<template>
  <button
    class="menu-item"
    :class="{ 'is-active': props.isActive ? props.isActive() : null, 'dynamic-width': !props.icon && !props.iconSrc }"
    @click="props.action"
    :title="props.title"
  >
    <svg v-if="props.icon && !props.iconSrc" class="remix">
      <use :xlink:href="`${remixiconUrl}#ri-${props.icon}`" />
    </svg>
    <img v-if="props.iconSrc" :src="props.iconSrc" class="custom-icon" />
    <span v-if="!props.icon && !props.iconSrc" class="button-label">{{ props.title }}</span>
  </button>
</template>

<script setup lang="ts">
  import remixiconUrl from 'remixicon/fonts/remixicon.symbol.svg'
  const props = defineProps<{
    icon: string
    title: string
    action: Function
    isActive?: Function
  }>()
</script>

<style lang="scss">
.menu-item {
  background: transparent;
  border: none;
  border-radius: 0.4em;
  color: #333;
  cursor: pointer;
  height: 2em;
  padding: 0.25em;
  margin-right: 0.5em;
  width: 1.75em;
  display: inline-flex;
  align-items: center;
  
  svg {
    
    fill: currentColor;
    height: 100%;
    width: 100%;
  }

  .custom-icon {
    display: flex;
    height: 1rem;
    width: 1rem;
  }

  .button-label {
    font-size: 0.875rem;
  }

  &.is-active,
  &:hover {
    background-color: #d6d6d6;
  }
}

.dynamic-width {
  width: auto;
  padding: 0.25rem 0.5rem;
}

.dynamic-width .button-label {
  white-space: nowrap;
}
</style>

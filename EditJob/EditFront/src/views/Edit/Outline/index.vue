<template>
  <div class="outline__list" style="display: flex; flex-direction: column;">
    <h2 class="text-gray-400">大纲</h2>
    <div class="outline__items">
    <template v-for="(heading, index) in headings" :key="index">
      <el-popover
        trigger="click"
        placement="right"
      >
        <template #reference>
          <el-button
            @click="handleHeadingClick(heading.text)"
            text
            class="outline__item"
            :class="`outline__item--${heading.level}`"
          >
            {{ heading.text }}
            <el-icon v-if="heading.icon"><component :is="heading.icon"/></el-icon>
          </el-button>
        </template>
        <!-- 如果需要弹出内容，请在这里添加 -->
      </el-popover>
    </template>
  </div>
</div>
</template>

<script setup lang="ts">
import { h, ref, type Component } from 'vue'

import { useEditorStore } from '@/store'
import { storeToRefs } from 'pinia'
import { watch } from 'vue';

const editorStore = useEditorStore()
const { headings } = storeToRefs(editorStore)


// 处理大纲点击事件
const handleHeadingClick = (headingText) => {
  editorStore.setActiveHeading(headingText);
};

const props = defineProps({
  note: {
    type: Object,
    required: true,
  },
});


// 解析 HTML 内容，提取出 heading 标签信息
const extractHeadings = (htmlContent) => {
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlContent, 'text/html');
  const headingElements = doc.querySelectorAll('h1, h2, h3, h4, h5, h6');
  return Array.from(headingElements).map(heading => ({
    level: parseInt(heading.tagName[1]), // 获取 heading 的级别 (1-6)
    text: heading.textContent.trim(), // 获取 heading 的文本内容
  }));
};

// 监听选中笔记的变化，当笔记变化时更新大纲内容
watch(
  () => props.note,
  (newNote) => {
    if (newNote && newNote.content) {
      // 从笔记内容中提取出大纲信息
      headings.value = extractHeadings(newNote.content);
    }
  },
  { immediate: true }
);

</script>



<style scoped lang="scss">
.outline {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  overflow: hidden;
  overflow-y: auto; /* 允许垂直滚动条 */
  z-index: 9; 
  opacity: 0.75;
  border-radius: 0.5rem;
  padding: 0.75rem;
  background: rgba(black, 0.1);



  &__list {
    display: flex;
    flex-direction: column;
    list-style: none;
    font-size: 18px;
    padding: 0;
    overflow-y: auto; /* 在需要时允许垂直滚动条 */
  }

  &__items {
    flex: 1; /* 填充剩余空间 */
    overflow-y: auto; /* 允许垂直滚动条 */
  }

  &__item {
    cursor: pointer;
    margin-bottom: 0.5rem;
    word-break: break-word; /* 自动换行 */
    &--1 {
      font-size: 23px;
    }
    &--3 {
      padding-left: 1rem;
    }
    &--4 {
      padding-left: 2rem;
    }
    &--5 {
      padding-left: 3rem;
    }
    &--6 {
      padding-left: 4rem;
    }
  }
}
</style>


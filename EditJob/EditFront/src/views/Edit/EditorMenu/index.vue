<template>
  <div class="top">
    <template v-for="(item, index) in items">
      <div
        class="divider"
        v-if="item.type === 'divider'"
        :key="`divider${index}`"
      />
      <MenuItem
        v-else
        :key="index"
        v-bind="item"
      />
    </template>
  <MenuItem icon="table-line" title="插入表格" :action="insertTable" />
  <MenuItem  icon="image-add-line" title="插入图片" :action="uploadImage" />
  <MenuItem icon="upload-line" title="上传文档" :action="uploadTemplate" />
  <MenuItem icon="download-fill" title="导出word文档" :action="exportTemplate" />

 <!-- AI Dropdown Menu -->
 <MenuItem icon="robot-2-fill" title="AI功能" @click="toggleDropdown" />
    <Teleport to="body">
      <div v-if="showDropdown" class="dropdown-content" :style="{ top: dropdownPosition.top + 'px', left: dropdownPosition.left + 'px' }">
        <div class="dropdown-item" @click="picOCR">
          <MenuItem icon="character-recognition-line" title="上传图片转文字" />
          <span class="itemwenzi">上传图片转文字</span>
        </div>
        <div class="dropdown-item" @click="videoToText">
          <MenuItem icon="video-fill" title="视频转文字" />
          <span class="itemwenzi">上传视频转文字</span>
        </div>
        <div class="dropdown-item" @click="voiceToText">
          <MenuItem icon="voice-recognition-line" title="语音转文字" />
          <span class="itemwenzi">上传语音转文字</span>
        </div>
        <div class="dropdown-item" @click="fullTextCorrection">
          <MenuItem icon="edit-line" title="全文校正" />
          <span class="itemwenzi">全文校正</span>
        </div>
      </div>
    </Teleport>

  <MenuItem icon="file-paper-2-fill" title="文献资料" :action="showliterature" />
  <MenuItem icon="save-3-line" title="保存" :action="saveDocument" />
  <MenuItem icon="git-repository-commits-fill" title="存为模板" :action="saveAsTemplate" />
  
  <MenuItem icon="file-text-fill" title="显示大纲" :action="showrighttools" />
  <MenuItem icon="user-fill" title="打开笔记列表" :action="showLeftSidebar" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Editor } from '@tiptap/vue-3'
import MenuItem from '@/views/Edit/MenuItem/index.vue'
import Italic from '@tiptap/extension-italic'
import Highlight from '@tiptap/extension-highlight'
import {
  CaretLeft,
  CaretBottom,
  CaretRight,
} from '@element-plus/icons-vue'

const showDropdown = ref(false);
const dropdownPosition = ref({ top: 0, left: 0 });

const toggleDropdown = (event: MouseEvent) => {
  showDropdown.value = !showDropdown.value;
  if (showDropdown.value) {
    dropdownPosition.value = {
      top: event.clientY,
      left: event.clientX
    };
  }
};

const props = defineProps<{ editor: Editor,
  uploadTemplate: () => void,
  exportTemplate: () => void, 
  uploadImage: () => void,
  insertTable: () => void,
  picOCR: () => void,
  videoToText: () => void,
  voiceToText: () => void,
  fullTextCorrection: () => void 
  showrighttools: () => void,
  setTextAlign: () => void,
  showLeftSidebar: () => void,
  showliterature: () => void,
  saveDocument: () => void,
  saveAsTemplate: () => void,
}>()


const items = [
  {
    icon: 'bold',
    title: '加粗',
    action: () => props.editor?.chain().focus().toggleBold().run(),
    isActive: () => props.editor?.isActive('bold')
  },
  {
    icon: 'italic',
    title: '斜体',
    action: () => props.editor?.chain().focus().toggleItalic().run(),
    isActive: () => props.editor?.isActive('italic')
  },
  {
    icon: 'strikethrough',
    title: '划线删除',
    action: () => props.editor?.chain().focus().toggleStrike().run(),
    isActive: () => props.editor?.isActive('strike')
  },
  {
    icon: 'code-view',
    title: '缩小字号（代码视图）',
    action: () => props.editor?.chain().focus().toggleCode().run(),
    isActive: () => props.editor?.isActive('code')
  },
  {
    icon: 'mark-pen-line',
    title: '高亮',
    action: () => props.editor?.chain().focus().toggleHighlight().run(),
    isActive: () => props.editor?.isActive('highlight')
  },
  {
    type: 'divider'
  },
  {
    icon: 'h-1',
    title: '一级标题',
    action: () =>
      props.editor?.chain().focus().toggleHeading({ level: 1 }).run(),
    isActive: () => props.editor?.isActive('heading', { level: 1 })
  },
  {
    icon: 'h-2',
    title: '二级标题',
    action: () =>
      props.editor?.chain().focus().toggleHeading({ level: 2 }).run(),
    isActive: () => props.editor?.isActive('heading', { level: 2 })
  },
  {
    icon: 'h-3',
    title: '三级标题',
    action: () =>
      props.editor?.chain().focus().toggleHeading({ level: 3 }).run(),
    isActive: () => props.editor?.isActive('heading', { level: 3 })
  },
  {
    icon: 'h-4',
    title: '四级标题',
    action: () =>
      props.editor?.chain().focus().toggleHeading({ level: 4 }).run(),
    isActive: () => props.editor?.isActive('heading', { level: 4})
  },
  {
    icon: 'paragraph',
    title: '文本样式',
    action: () => props.editor?.chain().focus().setParagraph().run(),
    isActive: () => props.editor?.isActive('paragraph')
  },
  {
    icon: 'list-unordered',
    title: '无序列表',
    action: () => props.editor?.chain().focus().toggleBulletList().run(),
    isActive: () => props.editor?.isActive('bulletList')
  },
  {
    icon: 'list-ordered',
    title: '有序列表',
    action: () => props.editor?.chain().focus().toggleOrderedList().run(),
    isActive: () => props.editor?.isActive('orderedList')
  },
  {
    icon: 'list-check-2',
    title: '任务栏',
    action: () => props.editor?.chain().focus().toggleTaskList().run(),
    isActive: () => props.editor?.isActive('taskList')
  },
  {
    icon: 'code-box-line',
    title: '插入代码',
    action: () => props.editor?.chain().focus().toggleCodeBlock().run(),
    isActive: () => props.editor?.isActive('codeBlock')
  },
  {
    type: 'divider'
  },
  {
    icon: 'double-quotes-l',
    title: '引用',
    action: () => props.editor?.chain().focus().toggleBlockquote().run(),
    isActive: () => props.editor?.isActive('blockquote')
  },
  {
    icon: 'separator',
    title: '水平线',
    action: () => props.editor?.chain().focus().setHorizontalRule().run()
  },
  {
    type: 'divider'
  },
  {
    icon: 'text-wrap',
    title: '换行',
    action: () => props.editor?.chain().focus().setHardBreak().run()
  },
  {
    icon: 'format-clear',
    title: '清除格式',
    action: () =>
      props.editor?.chain().focus().clearNodes().unsetAllMarks().run()
  },
  {
    type: 'divider'
  },
  {
    icon: 'arrow-go-back-line',
    title: '撤回',
    action: () => props.editor?.chain().focus().undo().run()
  },
  {
    icon: 'arrow-go-forward-line',
    title: '恢复',
    action: () => props.editor?.chain().focus().redo().run()
  },
  {
  icon: 'align-item-left-line',
  title: '左对齐',
  action: () => props.setTextAlign('left'),
  isActive: () => props.editor?.isActive({ textAlign: 'left' }),
},
{
  icon: 'align-item-vertical-center-line',
  title: '居中',
  action: () => props.setTextAlign('center'),
  isActive: () => props.editor?.isActive({ textAlign: 'center' }),
},
{
  icon: 'align-item-right-line',
  title: '右对齐',
  action: () => props.setTextAlign('right'),
  isActive: () => props.editor?.isActive({ textAlign: 'right' }),
},
]
</script>

<style lang="scss">
.divider {
  background-color: rgba(#fff, 0.25);
  display: inline-block;
}

.top {
  background-color: rgba(#fff, 0.25);
  display: flex;
}

.menu-item {
  position: relative;
  cursor: pointer; /* Ensure cursor changes to pointer on hover */
}

.dropdown-content {
  display: none;
  position: absolute;
  background-color: #f9f9f9;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
  z-index: 9999; /* Ensure it's on top */
}

.dropdown-content MenuItem {
  color: black;
  
  padding: 12px 16px;
  text-decoration: none;
  display: block;
}

.dropdown-content MenuItem:hover {
  background-color: #f1f1f1;
}

.itemwenzi {
  margin-left: 8px; /* Add some spacing between the icon and the text */
  font-size: 0.8rem; /* Make the font size smaller */
  color: #333; /* Adjust text color as needed */
  font-weight: bold; /* Make the font bold */
  text-align: center; /* Center the text */
}

/* Show the dropdown content when showDropdown is true */
.dropdown-content {
    display: grid;
    width: 30px;
}
</style>


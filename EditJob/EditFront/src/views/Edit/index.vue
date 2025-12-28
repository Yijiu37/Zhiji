<template>
  <div class="EditMain" ref="filecont" >
    <div id="loadingAnimation">
      <div class="loader">AI运行中...</div>
    </div>
    <ul @mousedown="see()" v-show="visiblemenu" :style="{ left: position.left + 'px', top: position.top + 'px', display: (visiblemenu ? 'grid' : 'none') }" class="contextmenu">
        <div class="item"  @click="polish()">
            <el-icon><Brush /></el-icon>
            润色
        </div>
        <div class="item" @click="continuation()">
            <el-icon><EditPen /></el-icon>
            续写
        </div>
        <div class="item" @click="fanyi()">
            <el-icon><EditPen /></el-icon>
            翻译
        </div>
        <div class="item" @click="zhaiyao()">
            <el-icon><EditPen /></el-icon>
            摘要
        </div>
        <div class="item" @click="sousuo()">
            <el-icon><EditPen /></el-icon>
            搜索
        </div>
        <div class="item" @click="tongji()">
            <el-icon><EditPen /></el-icon>
            可视化
        </div>
        <div class="item" @click="biaoge()">
            <el-icon><EditPen /></el-icon>
            表格
        </div>
    </ul>
    <div class="lefttools-wrapper" v-show="showNoteList">
    <div class="lefttools" >
      <!--关闭侧边栏按钮-->
    <button @click="toggleSidebar" class="leftSidebar-close-button" >x</button>
      <LeftTools @noteSelected="loadDetailNote" :userid="route.query.user_id" />
    </div>
  </div>
    <div class="editor-sum">
      <div class="document-header">
            <div class="document-name-info">
              <input v-model ="documentName" class='document-name' placeholder="请输入笔记名称" @input="updateDocumentName"></input>
              <span class="saved-time">最近更新日期: {{ lastSavedTime }}</span>
            </div>
            <div class="document-info">
              <button @click="saveDocument" class="save-button">保存</button>
              <button @click="toggleShareBox" class="share-button" title="分享给其他用户开启协同操作！">分享</button>
              <div v-if="showShareBox" class="share-box">
               <h3>共享文档</h3>
               <ul class="shared-users-list">
                 <li v-for="user in sharedUsers" :key="user.id" class="shared-user">
                   {{ user.username }}<span v-if="user.editing">（正在编辑中……）</span>
                 </li>                
               </ul>
               <input v-model="newUserId" placeholder="输入添加共享用户ID" />
               <button @click="addUser(newUserId)">添加</button>
               <button @click="toggleShareBox">关闭</button>
             </div>              
              <button @click="exitPage" class="exit-button">退出</button>
            </div>
          </div>
      <div class="editor">
        <div class="toptools">
          <div class="toolbar">
            <button @click="toggleFontDropdown" class="font-button">
              <i class="ri-font-family"></i>
            </button>
            <select v-model="selectedFontSize" @change="setFontSize">
              <option v-for="size in fontSizes" :key="size" :value="size">{{ size }}px</option>
            </select>
          </div>
          <div v-if="showFontDropdown" class="font-dropdown" :style="{ top: dropdownPosition.y + 'px', left: dropdownPosition.x + 'px' }">
            <div class="drag-handle" @mousedown="startDrag"></div>
            <div v-for="font in fonts" :key="font" :style="{ fontFamily: font }" @click="setFontFamily(font)" class="font-option">
              {{ font }}
            </div>
          </div>
          <EditorMenu  :editor="editor"
          :uploadTemplate="uploadTemplate"
          :exportTemplate="exportTemplate"
          :uploadImage="uploadImage"
          :insertTable="insertTable"
          :picOCR="picOCR"
          :fullTextCorrection="fullTextCorrection"
          :showrighttools="showrighttools"
          :setTextAlign="setTextAlign"
          :showLeftSidebar="showLeftSidebar"
          :showliterature="showliterature"
          :voiceToText="voiceToText"
          :saveDocument="saveDocument"
          :saveAsTemplate="saveAsTemplate"
          />
        </div>
        <div v-if="showFloating" class="floating-box" ref="floatingBox">
          <div class="floating-box-header" ref="floatingBoxHeader">
            <h3>相关文献资料</h3>
            <button @click="closeFloatingBox" class="close-button">×</button>
          </div>
          <div class="floating-box-content">
            <ul>
              <li v-for="item in literatureList" :key="item.url">
                <a :href="item.url" target="_blank">{{ item.text }}</a>
              </li>
            </ul>
            <p v-if="!literatureList.length">没有数据</p>
          </div>
        </div>
        <div class="editor-new">
        <div class="editorcard" >
        
        <div class="editcont" >
          <EditorContent
          @mousedown="notsee()"
          @mousemove="mousemove()" 
          @mouseup="selecttext($event)"
          :editor="editor"
        />
        </div>
       
        <div class="bottomcount">
          字数统计:
          {{ editor?.storage.characterCount.characters() }}
        </div>
      </div>
      <div class="righttools-wrapper" v-show="showOutline" >
        <div class="righttools">
        <div class="outline-container">
      <button @click="toggleOutline" class="outline-close-button" >×</button>
      <Outline :note="selectedNote"></Outline>
      </div>
    </div>
    </div>
      </div>
    </div>
    </div>
  </div>
  </template>

<script lang="ts" setup>
import axios from 'axios'; // 导入 axios 库
import { Brush, EditPen } from '@element-plus/icons-vue';
import { useRouter,useRoute } from 'vue-router';
import { defineComponent, ref, onMounted,onBeforeUnmount,watch,nextTick, reactive } from 'vue';
import { Editor, EditorContent, useEditor,BubbleMenu } from '@tiptap/vue-3';
import { storeToRefs } from 'pinia'
import Underline from '@tiptap/extension-underline'
import TextStyle from "@tiptap/extension-text-style"
import Highlight from '@tiptap/extension-highlight'
//列表
import ListItem from '@tiptap/extension-list-item';
import OrderedList from '@tiptap/extension-ordered-list';
import BulletList from '@tiptap/extension-bullet-list'
//代码
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'
import css from 'highlight.js/lib/languages/css'
import js from 'highlight.js/lib/languages/javascript'
import ts from 'highlight.js/lib/languages/typescript'
import html from 'highlight.js/lib/languages/xml'
import { common, createLowlight } from 'lowlight'
//使用piania
import { useEditorStore } from '@/store';
import EditorMenu from './EditorMenu/index.vue';
import LeftTools from './NoteMenu/index.vue';
import { defineStore } from 'pinia'
import { ElMessage } from 'element-plus';
import 'element-plus/dist/index.css';
import ElementPlus from 'element-plus'
//word作为模板形式
import { useStore } from 'vuex';
import mammoth from 'mammoth';
import { Document, Packer, Paragraph, TextRun , HeadingLevel, Table as DocTable, TableRow as DocTableRow, TableCell as DocTableCell} from 'docx';
import { saveAs } from 'file-saver';
//table
import Table from '@tiptap/extension-table';
import TableRow from '@tiptap/extension-table-row';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import { mergeAttributes } from '@tiptap/core';
//picture
import Image from '@tiptap/extension-image';
import { io } from 'socket.io-client';
//字数统计
import CharacterCount from '@tiptap/extension-character-count';
import Heading from '@tiptap/extension-heading'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder';
import { UndoRound, MoreHorizOutlined } from '@vicons/material'
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import Outline from './Outline/index.vue';
//其他
import { computed } from 'vue';
import { Extension } from "@tiptap/core";
import Resizable from 'v-resizable-directive';
import Italic from '@tiptap/extension-italic';
import { ElIcon } from 'element-plus';
import 'remixicon/fonts/remixicon.css';
//保存到模板库
import defaultTemplateAvatar from '@/assets/images/template_default.png';

const aipolish = ref('');
const aicontinuation = ref('');
const ailoading = ref(false); // 定义 ailoading
const ailist = ref([]);
const documentName = ref(''); // 绑定输入框的文档名称
const lastSavedTime = ref(''); // 绑定显示的保存时间
const showShareBox = ref(false);
const sharedUsers = ref(['1', '2']);
const newUserId = ref('');
const filecont = ref(null);
const visiblemenu = ref(false);
const position = ref({ top: 0, left: 0 });
let hasmove = ref(false);
let hisstring = '';
let selection = null;
const notes = computed(() => store.getters.getNotes);
const showOutline = ref(false);
const showNoteList = ref(false);
const lowlight = createLowlight()
lowlight.register({ html, ts, css, js })


// 使用vuex
const store = useStore();
const editorStore = useEditorStore();
const socket = io('http://localhost:3000');
const selectedNote = ref(null);
// 路由传递参数
const router = useRouter();
const route = useRoute();
const noteId = ref(route.query.note_id || null); // 获取路由中的 note_id 参数
const userId = ref(route.query.user_id || null); // 获取路由中的 user_id 参数

//文献资料
const showFloating = ref(false);
const literatureList = ref([]);
const floatingBox = ref(null);
const floatingBoxHeader = ref(null);

onMounted(() => {
  const savedUserId = localStorage.getItem('user_id');
  userId.value = route.query.user_id;
  noteId.value = route.query.note_id;

  console.log('user_id1:', userId.value);

  if (userId.value) {
    localStorage.setItem('user_id', userId.value);
  } else {
    userId.value = savedUserId;
  }

  if (noteId.value) {
    socket.emit('checkNote', noteId.value, userId.value); 
    loadDetailNote(noteId.value);
  } else {
    ElMessage.warning('请先创建笔记或打开一个笔记');
  }
  socket.on('updateSaveTime', (noteid, newSaveTime) => {
    if (noteid === noteId.value) {
      lastSavedTime.value = newSaveTime;
    }
  });
  socket.on('contentUpdate', (noteid, content, editorUserId, cursorPos) => {
    if (noteId.value == noteid ) {
      editor.value?.commands.setContent(content);
      loadHeadings();
      editor.value?.commands.setTextSelection(cursorPos);
      //updateCursor(editorUserId, cursorPos);
  } else {
      console.warn('Editor or editor.commands is undefined');
  }});
  socket.on('noteContent', (noteid, content) => {
    if (noteId.value==noteid){
      editor.value?.commands.setContent(content);
      loadHeadings()
    }
  });
  socket.on('cursorUpdate', (noteid, editorUserId, cursorPos, color) => {
    if(noteid==noteId.value){
        //updateCursor(editorUserId, cursorPos, color);
      }
  });
  socket.on('refreshPage', (noteid) => {
  if (noteId.value == noteid) {
    loadDetailNote(noteid);
  }
});
socket.on('editingUsers', (nid, editingUsers) => {
    if (nid === noteId.value) {
      sharedUsers.value = sharedUsers.value.map(user => ({
        ...user,
        editing: editingUsers.includes(user.id.toString())
      }));
    }
  }); 
  socket.on('updateeditingUsers', (nid, editingUsers) => {
    fetchSharedUsers();

  }); 
  socket.on('suceessinvite-get', (noteid, userid) => {
      if (noteid === noteId.value) {
        fetchSharedUsers();
        ElMessage.success("id为",userid,"的用户加入共享编辑");
      }
  });
  console.log('user_id2:', userId.value);
});

const refreshPage = () => {
  socket.emit('refreshNote', noteId.value);
};

socket.on('documentNameUpdateGet', (noteid, document) => {
      if (noteid === noteId.value) {
        documentName.value = document;
      }
  });

const updateDocumentName = async () => {
    try {
      //await store.dispatch('updateDocumentName', { noteId: noteId.value, documentName: documentName.value });
      console.log(noteId.value, documentName.value);
      socket.emit('documentNameUpdate', noteId.value, documentName.value);
    } catch (error) {
      console.error('更新笔记名称时出错', error);
    }
};

const updateCursor = (editorUserId, cursorPos, color) => {
  // 获取 editor 容器
  const editorContainer = document.querySelector('.editor-new');
  if (!editorContainer) {
    console.warn('Editor container not found');
    return;
  }
  // 获取 editor 中的光标元素
  let cursorElement = document.querySelector(`.cursor-${editorUserId}`);
  if (!cursorElement) {
    cursorElement = document.createElement('div');
    cursorElement.classList.add(`cursor-${editorUserId}`, 'cursor');
    cursorElement.style.position = 'absolute';
    cursorElement.style.backgroundColor = color;
    cursorElement.style.width = '2px'; // 光标宽度
    cursorElement.style.height = '20px'; // 光标高度
    cursorElement.style.zIndex = '1000';
    cursorElement.style.cursor = 'pointer';


    // 创建悬停时显示的文本元素
    const cursorText = document.createElement('span');
    cursorText.classList.add('cursor-text');
    cursorText.textContent = `编辑中: ${editorUserId}`;
    cursorText.style.position = 'absolute';
    cursorText.style.left = '5px';
    cursorText.style.top = '5px';
    cursorText.style.backgroundColor = 'white';
    cursorText.style.padding = '2px 5px';
    cursorText.style.border = '1px solid black';
    cursorText.style.display = 'none'; // 初始状态下隐藏

    cursorElement.appendChild(cursorText);

    cursorElement.addEventListener('mouseover', () => {
      cursorText.style.display = 'block';
    });
    cursorElement.addEventListener('mouseout', () => {
      cursorText.style.display = 'none';
    });

    editorContainer.appendChild(cursorElement);
  }

  // 获取 editor 容器的滚动位置
  const scrollTop = editorContainer.scrollTop;
  const scrollLeft = editorContainer.scrollLeft;

  // 假设 cursorPos 是相对于 editor 的位置，直接设置
  cursorElement.style.left = `${cursorPos.left + scrollLeft}px`;
  cursorElement.style.top = `${cursorPos.top + scrollTop}px`;
};


    // 登录后从本地取user_id，在Note_Menu中加载笔记列表
    // 点击对应笔记后，传递回来笔记id，在此页面的编辑框内加载笔记内容

     // 加载headings
     const loadHeadings = () => {
          const headings = [] as any[]
          if (!editor.value) return
          const transaction = editor.value.state.tr
          if (!transaction) return

          editor.value?.state.doc.descendants((node, pos) => {
            if (node.type.name === 'heading') {
              console.log(pos, node)
              const start = pos
              const end = pos + node.content.size
              // const end = pos + node
              const id = `heading-${headings.length + 1}`
              if (node.attrs.id !== id) {
                transaction?.setNodeMarkup(pos, undefined, {
                  ...node.attrs,
                  id
                })
              }

              headings.push({
                level: node.attrs.level,
                text: node.textContent,
                start,
                end,
                id
              })
            }
          })

          transaction?.setMeta('addToHistory', false)
          transaction?.setMeta('preventUpdate', true)

          editor.value?.view.dispatch(transaction)
          editorStore.setHeadings(headings)
      }

    const exitPage = () => {
      router.push('/bookShelfPage' );
   };

    const toggleSidebar = () => {
    showNoteList.value = !showNoteList.value;
    };

  const showLeftSidebar = () => {
    showNoteList.value = true;
  }
    
    const toggleOutline = () => {
    showOutline.value = !showOutline.value;
    };

  const showrighttools = () => {
    showOutline.value = true;
  }

   // 加载笔记详情
   const loadDetailNote = async(noteid) => {
  //这里要获取传递过来的笔记id
  noteId.value = noteid;
  console.log("加载笔记"+ noteid);
  if (!noteid) {
    console.warn('未找到笔记ID');
    return; // 如果没有笔记ID，不执行数据加载
  }
  try {
    const response = await axios.get(`http://127.0.0.1:5000/load-detailnotes/${noteid}`);
    const NoteData = response.data[0]; //返回的是该笔记的所有数据，返回的是一个数组

    if (!NoteData) {
      console.warn('未找到笔记数据');
      return;
    }

    // 加载笔记名称
    documentName.value = NoteData.document_name; 
    // 加载笔记内容
    if (editor) {
    //editor.value?.commands.setContent(NoteData.content);
    socket.emit('checkNote', noteid, userId.value);
    } else {
      console.warn('编辑器实例未初始化');
    }
    // 加载笔记保存时间
    lastSavedTime.value = NoteData.saved_time;

  } catch (error) {
    console.error('加载笔记数据时出错', error);
  }
};

//共享页面
      const toggleShareBox = async () => {
      showShareBox.value = !showShareBox.value;
      console.log(showShareBox.value)
      if (showShareBox.value) {
        fetchSharedUsers();
      }
    };

    //返回共享当前笔记的所有用户ID
    const fetchSharedUsers = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:5000/get-shared-users/${noteId.value}`);
        sharedUsers.value = response.data; 
        fetchEditingUsers();
        
      } catch (error) {
        console.error("Failed to fetch shared users", error);
      }
    };


    const fetchEditingUsers = () => {
      socket.emit('getEditingUsers', noteId.value);
    };
    const handleEditingUsers = (nid, editingUsers) => {
      if (nid === noteId.value) {
        sharedUsers.value = sharedUsers.value.map(user => ({
          ...user,
          editing: editingUsers.includes(user.id)
        }));
      }
    };

     const addUser = async (newUserId) => { //这里输入了新加入的用户ID
   try {
     const response = await axios.post('http://127.0.0.1:5000/add-user', {
       note_id: noteId.value,
       new_user_id: newUserId,
       current_user_id: userId.value
     });
     if (response.status === 200) {
       ElMessage.success("发送邀请成功");
       fetchSharedUsers();
     } else {
       console.error("Failed to add new user");
     }
   } catch (error) {
     console.error("Failed to add new user", error);
   }
 };

    // 显示加载动画
const showLoadingAnimation = () => {
  const loadingElement = document.getElementById('loadingAnimation');
  if (loadingElement) {
    loadingElement.style.display = 'flex';
  } else {
    console.error("加载动画元素未找到");
  }
};

const hideLoadingAnimation = () => {
  const loadingElement = document.getElementById('loadingAnimation');
  if (loadingElement) {
    loadingElement.style.display = 'none';
  } else {
    console.error("加载动画元素未找到");
  }
};


    //进行润色的函数
    const polish = () => {
  console.log("进入润色")
  ailoading.value = true;
  visiblemenu.value = false;
  let formData = new FormData();
  formData.append("username", "123456");
  formData.append("key", "685c4adc8ec11f954dd3828de8ad97c3b96646a1");
  formData.append("cont", hisstring); // 这里的 hisstring 是所选择的文本
  let url = 'http://127.0.0.1:5000/getpolish';
  let method = 'post';
  showLoadingAnimation();
  axios({
    method,
    url,
    data: formData,
  }).then(res => {
    console.log(res.data);
    if (res.data && res.data.answer) {
      const selection = editor.value.state.selection;
      const { from, to } = selection;

      hideLoadingAnimation();
      editor.value.commands.insertContentAt(to, `\n示例：`);
      let index = 0;
      const interval = 5; // 这里的延迟时间可以根据需要调整

      const insertText = () => {
        if (index < res.data.answer.length) {
          editor.value.commands.insertContentAt(to + index + 4, res.data.answer[index]);
          index++;
          setTimeout(insertText, interval); // 延迟后调用下一个字符的插入
        }
      };
      insertText();

      var tpcard1 = { "title": "ai辅助评审", "cont": hisstring, "review": res.data.answer };
      ailist.value.push(tpcard1);
      navigator.clipboard.writeText(res.data.answer);
    } else {
      console.error('API 返回了空数据');
      hideLoadingAnimation();
    }
    ailoading.value = false;
  }).catch(err => {
    console.error('API 请求失败:', err);
    hideLoadingAnimation();
    ailoading.value = false;
  });
}

    // 进行aireview
 const continuation = () => {
   ailoading.value = true
   visiblemenu.value = false;
   let formData = new FormData();
   formData.append("username", "123456");
   formData.append("key", "685c4adc8ec11f954dd3828de8ad97c3b96646a1");
   formData.append("cont", hisstring);
   let url = 'http://127.0.0.1:5000/getcontinuation';
   let method = 'post';
   showLoadingAnimation();
   axios({
     method,
     url,
     data: formData,
   }).then(res => {
     console.log(res.data);
     if (res.data && res.data.answer) {
      const selection = editor.value.state.selection;
      const { from, to } = selection;
      hideLoadingAnimation();
      editor.value.commands.insertContentAt(to, `\n示例：`);
      let index = 0;
      const interval = 5; // 这里的延迟时间可以根据需要调整

      const insertText = () => {
        if (index < res.data.answer.length) {
          editor.value.commands.insertContentAt(to + index + 4, res.data.answer[index]);
          index++;
          setTimeout(insertText, interval); // 延迟后调用下一个字符的插入
        }
      };
      insertText();

      var tpcard1 = { "title": "ai辅助评审", "cont": hisstring, "review": res.data.answer };
      ailist.value.push(tpcard1);
      navigator.clipboard.writeText(res.data.answer);
    } else {
      console.error('API 返回了空数据');
      hideLoadingAnimation();
    }
    ailoading.value = false;
   }).catch(err => {
     console.error('API 请求失败:', err);
     hideLoadingAnimation();
     ailoading.value = false;
   });
 }

 const fanyi = () => {
   ailoading.value = true;
   visiblemenu.value = false;
   let formData = new FormData();
   formData.append("username", "123456");
   formData.append("key", "685c4adc8ec11f954dd3828de8ad97c3b96646a1"); // 我的令牌
   formData.append("cont", hisstring);
   let url = 'http://127.0.0.1:5000/gettranslate';
   let method = 'post';
   showLoadingAnimation();
   axios({
     method,
     url,
     data: formData,
   }).then(res => {
     console.log(res.data);
     if (res.data && res.data.answer) {
      const selection = editor.value.state.selection;
      const { from, to } = selection;
      hideLoadingAnimation();
      editor.value.commands.insertContentAt(to, `\n`);
      let index = 0;
      const interval = 5; // 这里的延迟时间可以根据需要调整

      const insertText = () => {
        if (index < res.data.answer.length) {
          editor.value.commands.insertContentAt(to + index + 1, res.data.answer[index]);
          index++;
          setTimeout(insertText, interval); // 延迟后调用下一个字符的插入
        }
      };
      insertText();

      var tpcard1 = { "title": "ai辅助评审", "cont": hisstring, "review": res.data.answer };
      ailist.value.push(tpcard1);
      navigator.clipboard.writeText(res.data.answer);
    } else {
      console.error('API 返回了空数据');
      hideLoadingAnimation();
    }
    ailoading.value = false;
   });
 }

 const zhaiyao = () => {
   ailoading.value = true;
   visiblemenu.value = false;
   let formData = new FormData();
   formData.append("username", "123456");
   formData.append("key", "685c4adc8ec11f954dd3828de8ad97c3b96646a1"); // 我的令牌
   formData.append("cont", hisstring);
   let url = 'http://127.0.0.1:5000/getabstract';
   let method = 'post';
   showLoadingAnimation();
   axios({
     method,
     url,
     data: formData,
   }).then(res => {
     console.log(res.data);
     if (res.data && res.data.answer) {
      const selection = editor.value.state.selection;
      const { from, to } = selection;
      hideLoadingAnimation();
      editor.value.commands.insertContentAt(to, `\n示例：`);
      let index = 0;
      const interval = 5; // 这里的延迟时间可以根据需要调整

      const insertText = () => {
        if (index < res.data.answer.length) {
          editor.value.commands.insertContentAt(to + index + 4, res.data.answer[index]);
          index++;
          setTimeout(insertText, interval); // 延迟后调用下一个字符的插入
        }
      };
      insertText();

      var tpcard1 = { "title": "ai辅助评审", "cont": hisstring, "review": res.data.answer };
      ailist.value.push(tpcard1);
      navigator.clipboard.writeText(res.data.answer);
    } else {
      console.error('API 返回了空数据');
      hideLoadingAnimation();
    }
    ailoading.value = false;
   });
 }
 const tongji = async () => {
    ailoading.value = true;
    visiblemenu.value = false;
    let formData = new FormData();
    formData.append("username", "123456");
    formData.append("key", "685c4adc8ec11f954dd3828de8ad97c3b96646a1");
    formData.append("cont", hisstring);

    showLoadingAnimation();

    try {
      const response = await axios.post('http://127.0.0.1:5000/tongji', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const filename = response.data.filename; // 从后端获取文件名
      const imageUrl = `http://127.0.0.1:5000/uploads/${filename}`; // 构造图片URL

      const width = prompt("请输入图片宽度（像素）:", "600"); // 提示用户输入宽度
      const height = prompt("请输入图片高度（像素）:", "400"); // 提示用户输入高度

    // 将光标移动到文本末尾并插入新的文本
      editor.value?.chain().focus().insertContent(`${hisstring}\n<img src="${imageUrl}" width="${width}" height="${height}" />`).run();  } catch (err) {
      console.error('API 请求失败:', err);
    } finally {
      hideLoadingAnimation();
      ailoading.value = false;
    }
  }

  const biaoge= async () => { 
    ailoading.value = true;
    visiblemenu.value = false;
    let formData = new FormData();
    formData.append("username", "123456");
    formData.append("key", "685c4adc8ec11f954dd3828de8ad97c3b96646a1");
    formData.append("cont", hisstring);

    showLoadingAnimation();

    try {
      const response = await axios.post('http://127.0.0.1:5000/biaoge', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const tableHtml = response.data.table;
      console.log("bbb")
      console.log(tableHtml)
      editor.value?.chain().focus().insertContent(`${hisstring}${tableHtml}`).run();
      console.log(editor)
  } catch (err) {
      console.error('API 请求失败:', err);
    } finally {
      hideLoadingAnimation();
      ailoading.value = false;
    }
  }

  
const showliterature= async () => { 
  ailoading.value = true;
  visiblemenu.value = false;
  let formData = new FormData();
  formData.append("username", "123456");
  formData.append("key", "685c4adc8ec11f954dd3828de8ad97c3b96646a1");
  const editorContent = editor.value?.getHTML();
  const content = convertHtmlToContent(editorContent);
  formData.append("cont", editorContent);

  showLoadingAnimation();

  try {
    const response = await axios.post('http://127.0.0.1:5000/showliterature', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    literatureList.value = JSON.parse(response.data.literature);
    showFloating.value = true;
    
 } catch (err) {
    console.error('API 请求失败:', err);
  } finally {
    hideLoadingAnimation();
    ailoading.value = false;
    
  }
}

  const closeFloatingBox = () => {
    showFloating.value = false;
  };

  const dragElement = (el) => {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    
    const dragMouseDown = (e) => {
      e = e || window.event;
      e.preventDefault();
      pos3 = e.clientX;
      pos4 = e.clientY;
      document.onmouseup = closeDragElement;
      document.onmousemove = elementDrag;
    };

    const elementDrag = (e) => {
      e = e || window.event;
      e.preventDefault();
      pos1 = pos3 - e.clientX;
      pos2 = pos4 - e.clientY;
      pos3 = e.clientX;
      pos4 = e.clientY;
      el.style.top = (el.offsetTop - pos2) + "px";
      el.style.left = (el.offsetLeft - pos1) + "px";
    };

    const closeDragElement = () => {
      document.onmouseup = null;
      document.onmousemove = null;
    };

    el.onmousedown = dragMouseDown;
  };
 const sousuo = () => {
   if (hisstring && hisstring.trim() !== "") {
   const searchQuery = encodeURIComponent(hisstring);
   const searchUrl = `https://www.baidu.com/s?wd=${searchQuery}`;
   window.open(searchUrl, '_blank');
 } else {
   console.log('没有选中文本内容');
 }
 }

    // 获取选中的文字
    const selecttext= (e:MouseEvent)=>{
            selection = window.getSelection();
            if(selection!=null&&hisstring!=selection){
              var content = selection.toString();
              if(content!=""){
                  var rect = filecont.value.getBoundingClientRect();
                  visiblemenu.value = true
                  position.value.top =  e.clientY;
                  position.value.left =e.clientX;
                  hisstring=content
                }
            }
            else{
              hisstring=""
            }
      }
    //鼠标移动
    const mousemove=()=>{
            hasmove.value=true;
      }
    //鼠标点击
    const notsee=()=>{
      visiblemenu.value = false;
      selection=null;
      }
    const see=()=>{
            visiblemenu.value = true;
      }

    

// 保存编辑的文档内容
const saveDocument = async () => {
  const currentTime = new Date().toLocaleString();
  lastSavedTime.value = currentTime;
  const content = editor.value?.getHTML();
  const noteData = {
    note_id: noteId.value,
    document_name: documentName.value,
    content: content,
    saved_time: currentTime,
  };
  try {
    await store.dispatch('saveNote', noteData);
    await store.dispatch('loadNotes', userId.value); //刷新左侧笔记列表
    ElMessage.success('文档保存成功');
    socket.emit('updateSaveTime', noteId.value, currentTime);
  } catch (error) {
    console.error('保存文档时出错', error);
  }
};

// 保存到该用户模板库
const saveAsTemplate = async () => {
  try {
    // 获取当前笔记信息
    const noteResponse = await axios.get(`http://localhost:5000/load-noteInfo?note_id=${noteId.value}`);
    const noteData = noteResponse.data[0];
    if (!noteData) {
        console.log('未找到笔记数据！');
        return;
      }
    const coverUrl = noteData.note_cover_url;
    const content = editor.value?.getHTML();
    const TemplateData = {
      user_id: userId.value,
      name: documentName.value,
      content: content,
      cover_url: coverUrl,
    };

    // 保存模板
    const templateResponse = await fetch('http://localhost:5000/save_template', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(TemplateData),
    });

    if (templateResponse.ok) {
      ElMessage.success('模板保存成功');
    } else {
      throw new Error('保存模板失败');
    }
  } catch (error) {
    console.error('保存模板时出错', error);
    ElMessage.error('保存模板时出错');
  }
};


 // 图片大小
 const CustomImage = Image.extend({
   addAttributes() {
     return {
       ...this.parent?.(),
       width: {
         default: null,
         parseHTML: element => element.getAttribute('width'),
         renderHTML: attributes => {
           if (!attributes.width) {
             return {};
           }
           return {
             width: attributes.width,
           };
         },
       },
       height: {
         default: null,
         parseHTML: element => element.getAttribute('height'),
         renderHTML: attributes => {
           if (!attributes.height) {
             return {};
           }
           return {
             height: attributes.height,
           };
         },
       },
     };
   },
   renderHTML({ HTMLAttributes }) {
     return ['img', mergeAttributes(HTMLAttributes)];
   },
 });


 // 表格样式
 const CustomTable = Table.extend({
   renderHTML({ HTMLAttributes }) {
     return ['table', mergeAttributes(HTMLAttributes, { class: 'custom-table' }), 0];
   },
 });

 const uploadTemplate = () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.docx'; // 目前只接受word文档
  input.onchange = async (event) => {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const arrayBuffer = e.target?.result as ArrayBuffer;
        const { value: html } = await mammoth.convertToHtml({ arrayBuffer });
        editor.value?.chain().focus().insertContent(html).run();
      };
      reader.readAsArrayBuffer(file);
    }
  };
  input.click();
};

const exportTemplate = async () => {
  const editorContent = editor.value?.getHTML(); // 获取编辑器中的HTML内容
  if (editorContent) {
    // 将HTML内容转换为docx库能够识别的内容
    const content = convertHtmlToContent(editorContent);

    const doc = new Document({
      sections: [
        {
          properties: {},
          children: content,
        },
      ],
    });

    const blob = await Packer.toBlob(doc);
    saveAs(blob, 'document.docx');
  } else {
    alert('编辑器内容为空');
  }
};

const convertHtmlToContent = (html) => {
   const parser = new DOMParser();
   const doc = parser.parseFromString(html, "text/html");
   const elements = doc.body.childNodes;
   const content = [];
   elements.forEach((element) => {
     const parsedElement = parseElement(element);
     if (parsedElement) {
       content.push(parsedElement);
     }
   });
   return content;
 };

   const parseElement = (element) => {
   if (element.nodeType === Node.TEXT_NODE) {
     return new TextRun(element.textContent);
   } else if (element.nodeType === Node.ELEMENT_NODE) {
     const tagName = element.tagName.toLowerCase();
     switch (tagName) {
       case "h1":
         return new Paragraph({
           text: element.textContent,
           heading: HeadingLevel.HEADING_1,
         });
       case "h2":
         return new Paragraph({
           text: element.textContent,
           heading: HeadingLevel.HEADING_2,
         });
       case "h3":
         return new Paragraph({
           text: element.textContent,
           heading: HeadingLevel.HEADING_3,
         });
       case "p":
         return new Paragraph({
           children: parseChildNodes(element.childNodes),
         });
       case "table":
         return new DocTable({
           rows: parseTableRows(element),
         });
       default:
         return new Paragraph({
           children: [new TextRun(element.textContent)],
         });
     }
   }
 };

 const parseChildNodes = (nodes) => {
  const children = [];
  nodes.forEach((node) => {
    if (node.nodeType === Node.TEXT_NODE) {
      children.push(new TextRun(node.textContent));
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      const tagName = node.tagName.toLowerCase();
      const textRun = new TextRun({
        text: node.textContent,
        bold: tagName === "b" || tagName === "strong",
        italics: tagName === "i" || tagName === "em",
        // 添加其他样式
      });
      children.push(textRun);
    }
  });
  return children;
};

const parseTableRows = (table) => {
  const rows = [];
  table.querySelectorAll("tr").forEach((rowElement) => {
    const cells = [];
    rowElement.querySelectorAll("td").forEach((cellElement) => {
      cells.push(new DocTableCell({
        children: [new Paragraph(cellElement.textContent)],
      }));
    });
    rows.push(new DocTableRow({
      children: cells,
    }));
  });
  return rows;
};



const uploadImage = () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  input.onchange = async (event) => {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await axios.post('http://127.0.0.1:5000/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        const filename = response.data.filename; // 从后端获取文件名
        const url = `http://127.0.0.1:5000/uploads/${filename}`; // 构造图片URL

        const width = prompt("请输入图片宽度（像素）:", "600"); // 提示用户输入宽度
        const height = prompt("请输入图片高度（像素）:", "400"); // 提示用户输入高度

        editor.value?.chain().focus().setImage({ src: url, width, height }).run();
      } catch (error) {
        console.error('图片上传失败', error);
      }
    }
  };
  input.click();
};



const insertTable = () => {
  const rows = prompt("请输入表格行数:");
  const cols = prompt("请输入表格列数:");
  if (rows && cols) {
    editor.value?.chain().focus().insertTable({ rows: parseInt(rows), cols: parseInt(cols) }).run();
  }
};

const picOCR = () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  input.onchange = async (event) => {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await axios.post('http://127.0.0.1:5000/ocr', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.data && response.data.recognized_text) {
          const recognizedText = response.data.recognized_text.join('\n');
          // Assuming you want to insert the recognized text into an editor
          editor.value?.chain().focus().insertContent(recognizedText).run();
        } else {
          alert('OCR识别失败');
        }
      } catch (error) {
        console.error('OCR识别过程中发生错误:', error);
      }
    }
  };
  input.click();
};

// 全文矫正
const fullTextCorrection = async () => {
  ailoading.value = true;
  visiblemenu.value = false;
  let formData = new FormData();
  formData.append("username", "123456");
  formData.append("key", "685c4adc8ec11f954dd3828de8ad97c3b96646a1");
  
  // 获取编辑器中的所有文本内容
  const editorContent = editor.value?.getHTML();
  const content = convertHtmlToContent(editorContent);
  formData.append("cont", editorContent);

  let url = 'http://127.0.0.1:5000/completeAI';
  let method = 'post';
  showLoadingAnimation();

  try {
    const res = await axios({
      method,
      url,
      data: formData,
    });

    console.log(res.data);
    if (res.data && res.data.answer) {
      // 将后端返回的新文本结果显示在编辑器中，删去所有旧文本
      editor.value?.commands.setContent(res.data.answer);
      const tpcard1 = { "title": "ai辅助评审", "cont": content, "review": res.data.answer };
      ailist.value.push(tpcard1);

      // 确保文档是聚焦的
      window.focus();
      await navigator.clipboard.writeText(res.data.answer);
      //showMessage(); // 确认这个函数是否正确地显示了消息
    } else {
      console.error('API 返回了空数据');
    }
  } catch (err) {
    console.error('API 请求失败:', err);
  } finally {
    hideLoadingAnimation();
    ailoading.value = false;
  }
};



// 语音转文字
const voiceToText = () => {
  console.log('语音转文字进来了');
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'audio/wav'; // 接受wav格式的音频文件
  input.onchange = async (event) => {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        // 指向正确的后端路由
        const response = await axios.post('http://127.0.0.1:5000/voiceToText', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.data && response.data.transcribed_text) {
          const transcribedText = response.data.transcribed_text;
          // 将识别的文本插入编辑器
          editor.value?.chain().focus().insertContent(transcribedText).run();
        } else {
          alert('语音转文字失败');
        }
      } catch (error) {
        console.error('语音转文字过程中发生错误:', error);
      }
    }
  };
  input.click();
};

const setTextAlign = (alignment) => {
  editor.value?.chain().focus().setTextAlign(alignment).run();
};

const alignments = ref(['left', 'center', 'right']);
const TextAlign = Extension.create({
  name: "textAlign",
  // 添加内置变量
  addOptions() {
    return {
      types: [],
      alignments: ["left", "center", "right"],
      defaultAlignment: "left",
    };
  },
  // 添加属性
  addGlobalAttributes() {
    return [
      {
        types: this.options.types,
        attributes: {
          textAlign: {
            default: this.options.defaultAlignment,
            parseHTML: (element) => {
              console.log("parseHTML", element.style.textAlign);
              return element.style.textAlign || this.options.defaultAlignment;
            },
            renderHTML: (attributes) => {
              console.log("addGlobalAttributes", attributes.textAlign);
              return { style: `text-align: ${attributes.textAlign}` };
            },
          },
        },
      },
    ];
  },
  // 添加指令
  addCommands() {
    return {
      setTextAlign:
        (alignment) =>
        ({ commands }) => {
          if (!this.options.alignments.includes(alignment)) {
            return false;
          }
          console.log("types", commands.updateAttributes);
          return this.options.types.every((type) => commands.updateAttributes(type, { textAlign: alignment }));
        },

      unsetTextAlign:
        () =>
        ({ commands }) => {
          return this.options.types.every((type) => commands.resetAttributes(type, "textAlign"));
        },
    };
  },
  // 键盘快捷方式
  addKeyboardShortcuts() {
    return {
      "Mod-Shift-l": () => this.editor.commands.setTextAlign("left"),
      "Mod-Shift-e": () => this.editor.commands.setTextAlign("center"),
      "Mod-Shift-r": () => this.editor.commands.setTextAlign("right")      
    };
  },
});

const selectedFontSize = ref(16);
const fontSizes = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30];
const fonts = ['宋体', '黑体', '微软雅黑', '仿宋', '楷体', '华文宋体', 'Arial', 'Verdana', 'Courier New', 'Georgia', 'Times New Roman'];

const TextStyleExtended = TextStyle.extend({
  addAttributes() {
    return {
      ...this.parent?.(),
      fontSize: {
        default: null,
        parseHTML: (element) => element.style.fontSize.replace("px", ""),
        renderHTML: (attributes) => {
          if (!attributes.fontSize) {
            return {};
          }
          return {
            style: `font-size: ${attributes.fontSize}px`,
          };
        },
      },
      fontFamily: {
        default: null,
        parseHTML: (element) => element.style.fontFamily,
        renderHTML: (attributes) => {
          if (!attributes.fontFamily) {
            return {};
          }
          return {
            style: `font-family: ${attributes.fontFamily}`,
          };
        },
      },
    };
  },

  addCommands() {
    return {
      ...this.parent?.(),
      setFontSize:
        (fontSize) =>
        ({ commands }) => {
          return commands.setMark(this.name, { fontSize }); // this.name 值为 'textStyle'
        },
      unsetFontSize:
        () =>
        ({ chain }) => {
          return chain().setMark(this.name, { fontSize: null }).removeEmptyTextStyle().run(); // this.name 值为 'textStyle'
        },
      setFontFamily:
        (fontFamily) =>
        ({ commands }) => {
          return commands.setMark(this.name, { fontFamily }); // this.name 值为 'textStyle'
        },
      unsetFontFamily:
        () =>
        ({ chain }) => {
          return chain().setMark(this.name, { fontFamily: null }).removeEmptyTextStyle().run(); // this.name 值为 'textStyle'
        },
    };
  },
});

const setFontSize = () => {
  editor.value?.chain().focus().setFontSize(selectedFontSize.value).run();
};

const updateSelectedFontSize = () => {
  const selection = editor.value?.state.selection;
  if (selection.empty) {
    selectedFontSize.value = 16; // 默认值
    return;
  }

  const markAttrs = editor.value?.getAttributes('textStyle');
  const selectedFontSizes = new Set();
  
  editor.value.state.doc.nodesBetween(selection.from, selection.to, node => {
    if (node.marks) {
      node.marks.forEach(mark => {
        if (mark.type.name === 'textStyle' && mark.attrs.fontSize) {
          selectedFontSizes.add(mark.attrs.fontSize);
        }
      });
    }
  });

  if (selectedFontSizes.size === 1) {
    selectedFontSize.value = Array.from(selectedFontSizes)[0];
  } else {
    selectedFontSize.value = null; // 选中文本字号大小不统一时显示为空
  }
};



  const showFontDropdown = ref(false);

  const setFontFamily = (fontFamily) => {
    editor.value?.chain().focus().setFontFamily(fontFamily).run();
    showFontDropdown.value = false; // 选择字体后隐藏下拉框
  };

  // 拖拽下拉框
  const dropdownPosition = reactive({
    x: 0,
    y: 0,
    offsetX: 0,
    offsetY: 0,
    isDragging: false,
  });

  const toggleFontDropdown = (event) => {
    showFontDropdown.value = !showFontDropdown.value;
    if (showFontDropdown.value) {
      const rect = event.target.getBoundingClientRect();
      dropdownPosition.x = rect.left;
      dropdownPosition.y = rect.bottom;
    }
  };

  const startDrag = (event) => {
    dropdownPosition.isDragging = true;
    dropdownPosition.offsetX = event.clientX - dropdownPosition.x;
    dropdownPosition.offsetY = event.clientY - dropdownPosition.y;
    document.addEventListener('mousemove', onDrag);
    document.addEventListener('mouseup', stopDrag);
  };

  const onDrag = (event) => {
    if (dropdownPosition.isDragging) {
      dropdownPosition.x = event.clientX - dropdownPosition.offsetX;
      dropdownPosition.y = event.clientY - dropdownPosition.offsetY;
    }
  };

  const stopDrag = () => {
    dropdownPosition.isDragging = false;
    document.removeEventListener('mousemove', onDrag);
    document.removeEventListener('mouseup', stopDrag);
  };


// 使用ref创建可变的响应式引用
    // 编辑器初始化（先初始化再加载）
    const editor = useEditor({
  content: ``,
  extensions: [
  TextAlign.configure({
     types: ["heading", "paragraph"],
   }),
   TextStyleExtended,
   Italic,
   Highlight,
    StarterKit.configure({
      heading: {
        levels: [1, 2, 3, 4, 5],
      },
    }),
    TaskList,
    TaskItem,
    Placeholder.configure({
      placeholder: '开始输入文本 …'
    }),
    CustomImage,
    CustomTable.configure({
      resizable: true,
    }),
    TableRow,
    TableCell,
    TableHeader,
    OrderedList,
    BulletList,
    ListItem,
    CharacterCount.configure({
      limit: 10000
    })
  ],
  onCreate({ editor }) {
    loadHeadings();
    editorStore.setEditorInstance(editor);
    const cursorPos = editor.state.selection.$anchor.pos;
    socket.emit('cursorUpdate', noteId.value, userId.value, cursorPos);
  },
  onUpdate({ editor }) {
    if (editor && editor.state && editor.state.selection) {
      loadHeadings();
      const cursorPos = editor.state.selection.$anchor.pos;
      socket.emit('contentUpdate', noteId.value, editor.getHTML(), userId.value, cursorPos);
      socket.emit('cursorUpdate', noteId.value, userId.value, cursorPos);
      updateSelectedFontSize();
    } else {
      console.warn('Editor state or selection is undefined');
    }
  },
  injectCSS: false,
});

watch(editor, (newEditor) => {
  if (newEditor) {
    newEditor.on('selectionUpdate', updateSelectedFontSize);
  }
});

  </script>
  
  <style lang="scss">
  b {
    font-weight: bold;
  }

  .italic {
    font-style: italic;
  }

  .toolbar {
  display: flex;
  align-items: center;
  height: 2em;
}

.font-button {
  margin-right: 3px;
  height: 100%; /* 高度与工具栏一致 */
  width: 35px; /* 调整按钮宽度 */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0; /* 移除内边距 */
  border: none; /* 移除边框 */
  background: none; /* 移除背景 */
  cursor: pointer; /* 鼠标悬停时显示手型光标 */
}

.font-dropdown {
  position: absolute;
  max-width: 220px; /* 设置最大宽度 */
  max-height: 150px; /* 设置最大高度 */
  overflow-y: auto; /* 添加垂直滚动条 */
  background-color: white;
  border: 1px solid #ccc;
  z-index: 10;
}

.drag-handle {
  width: 100%;
  height: 20px; /* 设置拖拽区域的高度 */
  cursor: move; /* 鼠标悬停时显示拖拽光标 */
  background-color: #f0f0f0; /* 设置拖拽区域背景色 */
  border-bottom: 1px solid #ccc; /* 设置拖拽区域下边框 */
}

.font-option {
  padding: 5px 10px;
  cursor: pointer;
}

.font-option:hover {
  background-color: #f0f0f0;
}
  
  #loadingAnimation {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.2); /* 半透明背景 */
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000; /* 确保在最上层 */
    display: none; /* 默认隐藏 */
  }

  #loadingAnimation .loader {
    background: white;
    padding: 35px;
    border-radius: 40px;
    text-align: center;
    font-size: larger;
    letter-spacing: 3px
  }

  .expand-sidebar {
  position: fixed;
  top: 50%;
  left: 0;
  transform: translateY(-50%);
  padding: 10px;
  background-color: #3498db;
  color: white;
  cursor: pointer;
  border-radius: 0 5px 5px 0;
  box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
}

  
.EditMain {
  display: flex;
  width: 100%;
  height: 100%;
  background-color: #ffffff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  max-width: 100vw;
  max-height: 100vh;
  overflow: hidden;
}

.editor-sum {
  position: relative; /* 为子元素的绝对定位提供参考 */
  width: 100%;
  height: calc(100vh - 0px); /* 填满整个视口 */
  display: flex;
  flex-direction: column;
}

.toptools {
  background-color: rgba(207, 220, 245, 0.199);
  border-bottom: 1px dashed #9ca19f65;
  display: flex;
  height: 2em;
  width: 100%;
  box-shadow: inset 2px 2px 10px #e6e6e6, inset -2px -2px 10px #e6e6e6;
  border-radius: 2px;
  overflow: hidden; /* 防止内容溢出 */
}

.menu-item {
  background: transparent;
  border: none;
  border-radius: 0.4em;
  color: #333;
  cursor: pointer;
  height: 2em;
  padding: 0.25em;
  margin-right: 0.5em;
  width: auto; /* 让宽度随内容自适应 */
  flex: 1; /* 让菜单项根据容器的宽度调整 */
  display: inline-flex;
  align-items: center;
  justify-content: center; /* 居中对齐内容 */
}

.righttools-wrapper {
  position: absolute;
  right: 0;
  height: 100%;
  z-index: 1000; /* 确保大纲组件在最上层 */
}
.lefttools-wrapper {
  position: absolute;
  left: 0;
  height: 100%;
  z-index: 1000; /* 确保大纲组件在最上层 */
  border: 1px solid #ccc; /* 设置默认的边框 */
  border-right-width: 4px; /* 设置右边框的宽度 */
  border-right-color: #cdcdcd; /* 设置右边框的颜色 */
  overflow-y: auto; /* 确保内容超出时出现滚动条 */
  scrollbar-color: transparent; /* 滚动条初始隐藏 */
}

.righttools {
  background-color: #dcdcdc;
  width: 20vw; /* 使用绝对定位的宽度 */
  height: 100%; /* 相对父容器的高度 */
  position: relative; /* 内部元素相对于此容器定位 */
  resize: horizontal;
}
.lefttools {
  background-color: #dcdcdc;
  width: 18.5vw; /* 使用绝对定位的宽度 */
  height: 100%; /* 相对父容器的高度 */
  position: relative; 
}

.outline-container {
  position: absolute;
  top: 0;
  left: 10px;
  bottom: 0;
  right: 0;
  overflow-y: auto; /* 可选，处理内容溢出 */
}

.editor {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  //grid-column: 1 / 2;
}

.editorcard {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column; /* 设置为列方向排列 */
  border: 1px solid #4f5c5765;
  flex: 66%;
  background-color: #8a8a8a;
}

.document-name {
    display: flex;
    font-size: 1.5vw;
    border: none;
    outline: none;
    background: none;
    width: 100%;
    margin-left: 10px;
}


.editor-new{
  display: flex;
  flex: 95%; /* 占比 5% */
}

.editcont {
    overflow-y: auto;
    overflow-x: hidden;
    width: 60%;
    align-self: center;
    flex-grow: 1;
    flex-shrink: 0;
    flex-basis: 0;
    background-color: #ffffff;
}
.saved-time {
    margin-left: 1vw;
    font-size: 1vw;
    bottom: 0;
    left: 0;
}

.note-name{
    font-weight: bold;
    font-size: small;
}

.bottomcount {
  background-color: rgba(207, 220, 245, 0.199);
  border-top: 1px dashed #9ca19f65;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 3%; /* 占比 3% */
  flex-shrink: 0; /* 确保bottomcount不会缩小 */
}

.el-button.is-text {
    display: flex;
    align-items: center;
    background-color: transparent;
    border: 0 solid transparent;
    color: var(--el-button-text-color);
    text-align: left; /* 文字左对齐 */
    justify-content: flex-start; /* 确保文本在按钮内左对齐 */
    padding-left: 10px; /* 移除左侧的默认内边距 */
}

.outline-close-button {
    border-radius: 8px;
    border: 1px solid transparent;
    padding: 0.6em 1.2em;
    font-size: 1em;
    font-weight: 500;
    font-family: inherit;
    background-color: transparent; /* 去掉背景颜色 */
    cursor: pointer;
    transition: border-color 0.25s;
    float: right; /* 将按钮靠右对齐 */
}

.leftSidebar-close-button {
    position: absolute; /* 绝对定位 */
    border-radius: 8px;
    border: 1px solid transparent;
    padding: 0.6em 1.2em;
    font-size: 1em;
    font-weight: 500;
    font-family: inherit;
    background-color: transparent; /* 去掉背景颜色 */
    cursor: pointer;
    transition: border-color 0.25s;
    float: left; /* 将按钮靠右对齐 */
    z-index: 1000; /* 确保按钮在其他元素之上 */
}
  
  .ProseMirror {
    box-sizing: border-box; // 确保 padding 和 border 不会增加元素的实际尺寸
    overflow-y: auto; // 确保内容在容器内滚动
    margin-left: 20px; /* 左边距 */
    margin-right: 20px; /* 右边距 */
    margin-top: 10px; /* 上边距 */
  }
  .ProseMirror p {
    margin: 0;
  }
  .ProseMirror:focus {
    outline: none;
  }
  .tiptap p.is-editor-empty:first-child::before {
    color: #adb5bd;
    content: attr(data-placeholder);
    float: left;
    height: 0;
    pointer-events: none;
  }
  
  .tiptap {
    > * + * {
      margin-top: 0.75em;
    }
  
    ul {
      padding: 0 2rem;
      list-style: square;
    }
    ol {
      padding: 0 2rem;
      list-style: decimal;
    }
    table {
      border-collapse: collapse;
      table-layout: fixed;
      width: 100%;
      margin: 0;
      overflow: hidden;
  
      td,
      th {
        min-width: 1em;
        border: 2px solid #ced4da;
        padding: 3px 5px;
        vertical-align: top;
        box-sizing: border-box;
        position: relative;
  
        > * {
          margin-bottom: 0;
        }
      }
      
  
      th {
        font-weight: bold;
        text-align: left;
        background-color: #f1f3f5;
      }
  
      .selectedCell:after {
        z-index: 2;
        position: absolute;
        content: '';
        left: 0;
        right: 0;
        top: 0;
        bottom: 0;
        background: rgba(200, 200, 255, 0.4);
        pointer-events: none;
      }
  
      .column-resize-handle {
        position: absolute;
        right: -2px;
        top: 0;
        bottom: -2px;
        width: 4px;
        background-color: #adf;
        pointer-events: none;
      }
  
      p {
        margin: 0;
      }
    }
    pre {
      background: #0d0d0d;
      color: #fff;
      font-family: 'JetBrainsMono', monospace;
      padding: 0.75rem 1rem;
      border-radius: 0.5rem;
  
      code {
        color: inherit;
        padding: 0;
        background: none;
        font-size: 0.8rem;
      }
  
      .hljs-comment,
      .hljs-quote {
        color: #616161;
      }
  
      .hljs-variable,
      .hljs-template-variable,
      .hljs-attribute,
      .hljs-tag,
      .hljs-name,
      .hljs-regexp,
      .hljs-link,
      .hljs-name,
      .hljs-selector-id,
      .hljs-selector-class {
        color: #f98181;
      }
      .hljs-number,
      .hljs-meta,
      .hljs-built_in,
      .hljs-builtin-name,
      .hljs-literal,
      .hljs-type,
      .hljs-params {
        color: #fbbc88;
      }
  
      .hljs-string,
      .hljs-symbol,
      .hljs-bullet {
        color: #b9f18d;
      }
  
      .hljs-title,
      .hljs-section {
        color: #faf594;
      }
  
      .hljs-keyword,
      .hljs-selector-tag {
        color: #70cff8;
      }
  
      .hljs-emphasis {
        font-style: italic;
      }
  
      .hljs-strong {
        font-weight: 700;
      }
    }
  }
  
  .tableWrapper {
    overflow-x: auto;
  }
  
  .resize-cursor {
    cursor: ew-resize;
    cursor: col-resize;
  }
  .contextmenu {
    width: 120px;
    margin: 0;
    background: #fff;
    z-index: 3000;
    position: absolute;
    list-style-type: none;
    padding:5px;
    padding-left: 15px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 400;
    color: #333;
    box-shadow: 1px 1px 2px 1px rgba(0, 0, 0, 0.3);
    display: grid;
    grid-template-columns:50% 50%;

  }
  .contextmenu .item {
      height: 35px;
      width:100%;
      line-height: 35px;
      color: rgb(29, 33, 41);
      cursor: pointer;
    }
    .contextmenu .item {
      height: 35px;
      width:100%;
      line-height: 35px;
      color: rgb(29, 33, 41);
      cursor: pointer;
    }

    .contextmenu .item:hover {
      background: rgb(229, 230, 235);
    }
  </style>



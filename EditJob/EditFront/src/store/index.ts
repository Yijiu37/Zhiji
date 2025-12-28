import { defineStore } from 'pinia';
import { ref } from 'vue';
import { createStore } from 'vuex';
import axios from 'axios';

// 定义 Pinia 的 store
export const mainStore = defineStore('main', {
  state: () => {
    return {
      helloPinia: '你好 Pinia!',
    };
  },
  getters: {},
  actions: {},
});

export const useEditorStore = defineStore('editor', () => {
  const headings = ref();
  const activeHeading = ref();
  const editorInstance = ref();
  const userId = ref(sessionStorage.getItem('user_id') || null);
  const setHeadings = (data) => {
    headings.value = data;
  };
  const setActiveHeading = (headingText) => {
    if (editorInstance.value) {
      const editor = editorInstance.value;
      const { view, state } = editor;
      const { doc } = state;
  
      // 查找对应的 heading 节点
      let targetPos = null;
      doc.descendants((node, pos) => {
        if (node.type.name.startsWith('heading') && node.textContent.trim() === headingText.trim()) {
          targetPos = pos;
          return false; // 找到目标后停止遍历
        }
      });
     // 确保编辑器的 DOM 元素获得焦点
     view.dom.focus();
      if (targetPos !== null) {
        view.dispatch(
          view.state.tr.setSelection(
            view.state.selection.constructor.near(view.state.doc.resolve(targetPos))
          ).scrollIntoView()
        );
        view.focus();
      }
    } else {
      console.warn('编辑器实例未初始化');
    }
  };
  const setEditorInstance = (data) => {
    console.log(editorInstance.value);
    editorInstance.value = data;
  };
  const setUserId = (id) => {
    sessionStorage.setItem('user_id', id);
    userId.value = id;
  };
  const getUserId = () => {
    return userId.value;
  };
  return {
    userId,
    headings,
    setHeadings,
    activeHeading,
    setActiveHeading,
    editorInstance,
    setEditorInstance,
    setUserId,
    getUserId,
  };
});

// 定义 Vuex 的 store
const vuexStore = createStore({
  state: {
    folders: [],
    notes: [],
  },
  mutations: {
    setFolders(state, folders) {
      state.folders = folders;
    },
    setNotes(state, notes) {
      state.notes = notes;
    },
    updateNote(state, updatedNote) {
      const folder = state.folders.find(folder => folder.id === updatedNote.folder_id);
      if (folder) {
        const noteIndex = folder.notes.findIndex(note => note.id === updatedNote.id);
        if (noteIndex !== -1) {
          folder.notes.splice(noteIndex, 1, updatedNote);
        }
      }
    },
  },
  actions: {
    async loadNotes({ commit }, userId) {
      try {
        const response = await axios.get(`http://127.0.0.1:5000/load-notes/${userId}`);
        commit('setFolders', response.data.folders);
        const notes = response.data.folders.flatMap(folder => folder.notes);
        commit('setNotes', notes);
      } catch (error) {
        console.error('加载笔记失败', error);
        throw error; // 可以选择抛出错误，由调用方处理
      }
    },
    async saveNote({ commit }, noteData) {
      try {
        const response = await axios.post('http://127.0.0.1:5000/update-note', noteData);
        commit('updateNote', noteData); // 更新笔记内容
        return response.data; // 返回保存成功的响应数据
      } catch (error) {
        console.error('保存笔记失败', error);
        throw error; // 可以选择抛出错误，由调用方处理
      }
    },
  },
  getters: {
    getNotes(state) {
      return state.notes;
    },
    getFolders(state) {
      return state.folders;
    },
  },
});

export default vuexStore;


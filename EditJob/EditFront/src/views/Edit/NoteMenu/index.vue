<template>
  <div class="menu">
    <div class="profile-pic-container" @click="navigateToProfile">
      <img :src="profileAvatar" class="profile-pic" />
    </div>
    <div class="note-management">
      <!-- 新建按钮 -->
      <div class="new-note" @click="showCreateOptionsDialog">
        新建
      </div>
      <!-- 选择操作对话框 -->
      <el-dialog v-model="createOptionsDialogVisible" title="选择操作" :append-to-body="true">
        <el-button type="primary" @click="showCreateFolderDialog">新建文件夹</el-button>
        <el-button type="primary" @click="showCreateDialog">新建笔记</el-button>
      </el-dialog>

      <!-- 新建文件夹对话框 -->
      <el-dialog v-model="createFolderDialogVisible" title="创建新文件夹" :append-to-body="true">
        <el-form :model="newFolder">
          <el-form-item label="文件夹名称">
            <el-input v-model="newFolder.name"></el-input>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="createFolderDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createFolder">确定</el-button>
        </template>
      </el-dialog>

      <!-- 新建笔记对话框 -->
      <el-dialog v-model="createDialogVisible" title="创建新笔记" :append-to-body="true">
        <el-form :model="newNote">
          <el-form-item label="笔记名称">
            <el-input v-model="newNote.name"></el-input>
          </el-form-item>
          <el-form-item label="笔记封面">
            <el-upload
              class="upload-demo"
              drag
              action="http://127.0.0.1:5000/upload"
              :auto-upload="false"
              :on-change="handleFileChange"
              :file-list="fileList"
              list-type="picture"
              :limit="1"
            >
              <i class="el-icon-upload"></i>
              <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            </el-upload>
          </el-form-item>
          <el-form-item label="文件夹">
            <el-select v-model="newNote.folder_id" placeholder="选择文件夹">
              <el-option
                v-for="folder in folders"
                :key="folder.id"
                :label="folder.folder_name"
                :value="folder.id"
              ></el-option>
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="uploadFile">确定</el-button>
        </template>
      </el-dialog>

      <!-- 文件夹和笔记列表 -->
      <div v-for="folder in folders" :key="folder.id" class="folder-item">
        <div class="folder-header">
          <img :src="FolderIcon" class="folder-icon" alt="Folder"/>
          <span class="folder-name">{{ folder.folder_name }}</span>
          <!--文件夹下拉列表操作-->
          <div class="folder-actions">
          <el-dropdown @command="handleFolderCommand(folder.id, $event)">
            <span class="el-dropdown-link" style="outline: none">
              ：<i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <template #dropdown>
              <el-dropdown-menu >
                <el-dropdown-item command="top">置顶</el-dropdown-item>
                <el-dropdown-item command="untop">取消置顶</el-dropdown-item>
                <el-dropdown-item command="changeInfo">修改文件夹</el-dropdown-item>
                <el-dropdown-item command="delete">删除文件夹</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

          <el-icon 
            class="dropdown-button" @click.stop="toggleFolder(folder.id, $event)" >
            <component :is="getIconComponent(folder.id)" />
          </el-icon>
        </div>
        <div v-if="folderOpen[folder.id]" class="folder-content">
          <div v-for="note in folder.notes" :key="note.id" class="note-item" @click="openNoteDetail(note.id)">
            <div class="note-title">
              <div class="note-cover">
                <img :src="note.note_cover_url" class="note-cover"/>
              </div>
              <div class="note-info">
                <div class="note-name">{{ note.document_name }}</div>
                <div class="note-date">{{ note.saved_time }}</div>
              </div>
            </div>
            <div class="note-actions">
              <el-dropdown @command="handleCommand(note.id, $event)">
                <span class="el-dropdown-link" style="outline: none">
                  ：<i class="el-icon-arrow-down el-icon--right"></i>
                </span>
                <template #dropdown>
                  <el-dropdown-menu >
                    <el-dropdown-item command="top">置顶</el-dropdown-item>
                    <el-dropdown-item command="untop">取消置顶</el-dropdown-item>
                    <el-dropdown-item command="changeInfo">修改信息</el-dropdown-item>
                    <el-dropdown-item command="delete">删除</el-dropdown-item>
                    <el-dropdown-item command="duplicate">复制</el-dropdown-item>
                    <el-dropdown-item command="move">移动</el-dropdown-item>
                    <el-dropdown-item command="export">导出</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-icon v-if="!note.is_favorite" class="el-icon-star" @click="toggleStar(note.id)"><Star /></el-icon>
              <el-icon v-else class="el-icon-star" @click="toggleStar(note.id)"><StarFilled /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { ref, onMounted, computed  } from 'vue';
import { ElMessage,ElMessageBox } from 'element-plus';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import axios from 'axios';
import 'element-plus/dist/index.css';
import defaultAvatar from '@/assets/images/touxiang.png';
import { CaretBottom, CaretRight } from '@element-plus/icons-vue';
import FolderIcon from '@/assets/images/folder.svg'; // 文件夹图标
import { Document, Packer, Paragraph, TextRun } from 'docx';
import { saveAs } from 'file-saver';
import { io } from 'socket.io-client';
const socket = io('http://localhost:3000');


export default {
  name: 'LeftTools',
  emits: ['noteSelected'],
  props: {
    onNoteSelect: {
      type: Function,
      required: true
    },
    userid: {
      type: String,
      required: true
    },
  },
  setup(props, { emit }) {
    const router = useRouter();
    const store = useStore();
    const profileAvatar = ref('');
    const userId = ref(props.userid);
    const createDialogVisible = ref(false);
    const createFolderDialogVisible = ref(false);
    const createOptionsDialogVisible = ref(false);

    // 判断文件夹是否展开
    const isOpen = (id) => openFolderId.value === id;
    // 当前展开的文件夹ID
    const openFolderId = ref(null);
    const newNote = ref({
      name: '',
      cover: '',
      date: new Date().toLocaleString(),
      isstarred: false,
      folder_id: null
    });
    const newFolder = ref({
      name: ''
    });
    const fileList = ref([]);
    const folderOpen = ref({});
    //获得笔记和文件夹
    const notes = computed(() => store.getters.getNotes);
    const folders = computed(() => store.getters.getFolders);

    const navigateToProfile = () => {
      router.push({ path: '/PersonalPage', query: { user_id: userId.value } });
    };

    // 展示选择操作对话框
    const showCreateOptionsDialog = () => {
      createOptionsDialogVisible.value = true;
    };

    // 展示新建文件夹对话框
    const showCreateFolderDialog = () => {
      createOptionsDialogVisible.value = false;
      createFolderDialogVisible.value = true;
    };

    // 展示新建笔记对话框
    const showCreateDialog = () => {
      createOptionsDialogVisible.value = false;
      createDialogVisible.value = true;
    };

    // 创建新文件夹
    const createFolder = () => {
      if (!newFolder.value.name) {
        ElMessage.error('请填写文件夹名称');
        return;
      }

      axios.post('http://127.0.0.1:5000/create-folder', {
        user_id: userId.value,
        folder_name: newFolder.value.name
      })
      .then(response => {
        folders.value.push({
          id: response.data.folder_id,
          folder_name: newFolder.value.name,
          notes: []
        });
        createFolderDialogVisible.value = false;
        ElMessage.success('新建文件夹成功');
      })
      .catch(error => {
        console.error('新建文件夹失败:', error);
        ElMessage.error('新建文件夹失败');
      });
    };

    socket.on('updateSaveTime', (noteid, newSaveTime) => {
  // 找到对应的笔记并更新保存时间
  const note = notes.value.find(note => note.id === noteid);
  if (note) {
    note.saved_time = newSaveTime;
  }
  });
  socket.on('documentNameUpdateGet', (noteId, documentName) => {
    const note = notes.value.find(note => note.id === noteId);
    if (note) {
      note.document_name = documentName;
    }
});

    // 处理文件变化
    const handleFileChange = (file, fileListRef) => {
      if (fileListRef.length > 1) {
        fileListRef.splice(0, fileListRef.length - 1);
      }
      fileList.value = fileListRef;
      if (fileList.value.length > 0 && fileList.value[0].raw) {
        newNote.value.cover = URL.createObjectURL(fileList.value[0].raw);
      } else {
        newNote.value.cover = '';
      }
    };

    // 展开或折叠文件夹
  const toggleFolder = (folderId, event) => {
  // 如果是从图标点击触发，则进行文件夹展开/折叠操作
  if (event && event.target.closest('.dropdown-button')) {
    openFolderId.value = openFolderId.value === folderId ? null : folderId;
    if (folderOpen.value[folderId]) {
      delete folderOpen.value[folderId];
    } else {
      folderOpen.value[folderId] = true;
    }
  }
};



    //切换文件夹下拉按钮
    const getIconComponent = (id) => {
      return isOpen(id) ? CaretRight : CaretBottom;
    };

    // 创建新笔记
    const uploadFile = () => {
      if (!newNote.value.name || !newNote.value.cover || !newNote.value.folder_id) {
        ElMessage.error('请填写完整的信息并上传封面和选择文件夹');
        return;
      }
      const formData = new FormData();
      formData.append('file', fileList.value[0]?.raw);
      axios.post('http://127.0.0.1:5000/upload', formData)
        .then(response => {
          newNote.value.cover = `http://127.0.0.1:5000/uploads/${response.data.filename}`;
          saveNoteToDB(); // 保存到数据库
        })
        .catch(error => {
          console.error('上传失败:', error);
          ElMessage.error('上传失败');
        });
    };

    const saveNoteToDB = () => {
      axios.post('http://127.0.0.1:5000/save-note', {
        user_id: userId.value,
        document_name: newNote.value.name,
        note_cover_url: newNote.value.cover,
        saved_time: newNote.value.date,
        folder_id: newNote.value.folder_id
      })
        .then(response => {
          const folder = folders.value.find(folder => folder.id === newNote.value.folder_id);
          if (folder) {
            folder.notes.push({ ...newNote.value, id: response.data.note_id }); //把笔记加入文件夹
          }
          createDialogVisible.value = false;
          ElMessage.success('新建笔记成功');
          fileList.value = [];
          loadNotes(); // 刷新页面
        })
        .catch(error => {
          console.error('保存笔记失败:', error);
          ElMessage.error('保存笔记失败');
        });
    };

    // 处理命令
    const handleCommand = (noteId, command) => {
      switch (command) {
        case 'top':
          topNote(noteId);
          break;
        case 'untop':
          unTopNote(noteId);
          break;
        case 'delete':
          deleteNote(noteId);
          break;
        case 'export':
          exportNote(noteId);
          break;
        default:
          ElMessage.info(`执行命令: ${command}, 笔记ID: ${noteId}`);
      }
    };

    //文件夹处理操作
    const handleFolderCommand = (folderId, command) => {
      switch (command) {
        case 'top':
          // 处理置顶操作
          break;
        case 'untop':
          // 处理取消置顶操作
          break;
        case 'changeInfo':
          // 处理修改文件夹信息操作
          break;
        case 'delete':
          // 处理删除文件夹操作
          break;
        default:
          break;
        }
    };

    //置顶笔记
    const topNote = (noteId) => {
  axios.post('http://127.0.0.1:5000/top-note', { note_id: noteId })
    .then(response => {
      if (response.data.message === '笔记置顶成功') {
        let found = false;
        // 遍历文件夹
        for (const folder of folders.value) {
          const noteIndex = folder.notes.findIndex(note => note.id === noteId);

          if (noteIndex !== -1) {
            const [topNote] = folder.notes.splice(noteIndex, 1);
            folder.notes.unshift(topNote);
            found = true;
            break; // 找到并处理后退出循环
          }
        }

        if (found) {
          ElMessage.success('笔记置顶成功');
        } else {
          ElMessage.error('笔记未找到');
        }
      } else {
        ElMessage.error('置顶笔记时出错: ' + response.data.message);
      }
    })
    .catch(error => {
      console.error('置顶笔记时出错:', error);
      ElMessage.error('置顶笔记时出错: ' + error.message);
    });
};

// 取消置顶笔记
const unTopNote = (noteId) => {
  axios.post('http://127.0.0.1:5000/untop-note', { note_id: noteId })
    .then(response => {
      if (response.data.message === '笔记取消置顶成功') {
        let found = false;

        // 遍历文件夹
        for (const folder of folders.value) {
          const noteIndex = folder.notes.findIndex(note => note.id === noteId);

          if (noteIndex !== -1) {
            // 修改笔记状态
            folder.notes[noteIndex].is_top = 0;

            // 从当前文件夹的置顶位置移除笔记，并将其添加到数组末尾
            const [unTopNote] = folder.notes.splice(noteIndex, 1);
            folder.notes.push(unTopNote);

            found = true;
            break; // 找到并处理后退出循环
          }
        }

        if (found) {
          loadNotes(); // 刷新页面
          ElMessage.success('笔记取消置顶成功');
        } else {
          ElMessage.error('笔记未找到');
        }
      } else {
        ElMessage.error('取消置顶笔记时出错: ' + response.data.message);
      }
    })
    .catch(error => {
      console.error('取消置顶笔记时出错:', error);
      ElMessage.error('取消置顶笔记时出错: ' + error.message);
    });
};

    // 删除笔记
const deleteNote = (noteId) => {
  ElMessageBox.confirm(
    '此操作将永久删除该笔记, 是否继续?',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    axios.post('http://127.0.0.1:5000/delete-note', { note_id: noteId , user_id: userId.value})
      .then(response => {
        if (response.data.message === '笔记删除成功') {
          store.dispatch('loadNotes', userId.value); // 刷新笔记列表
          ElMessage.success('笔记删除成功');
        } else {
          ElMessage.error('删除笔记时出错: ' + response.data.message);
        }
      })
      .catch(error => {
        console.error('删除笔记时出错:', error);
        ElMessage.error('删除笔记时出错: ' + error.message);
      });
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
};


    // 收藏或取消收藏笔记，修改 is_favorite 属性
    const toggleStar = (noteId) => {
      event.stopPropagation();
      // 查找笔记
      let note;
      for (const folder of folders.value) {
        note = folder.notes.find(note => note.id === noteId);
        if (note) break;
      }
      if (note) {
        note.is_favorite = !note.is_favorite; // 收藏或取消收藏
        axios.post('http://127.0.0.1:5000/update-favorite', {
          note_id: noteId,
          is_favorite: note.is_favorite ? 1 : 0
        })
          .then(() => {
            ElMessage.info(`收藏/取消收藏 笔记ID: ${noteId}`);
            loadNotes(); // 刷新页面
          })
          .catch(error => {
            console.error('更新收藏状态失败:', error);
            ElMessage.error('更新收藏状态失败');
          });
      }
    };

    // 打开对应的笔记，加载笔记内容
    const openNoteDetail = (noteId) => {
      localStorage.setItem('note_id', noteId);
      emit('noteSelected', noteId);
    };

    // 加载用户的笔记列表
    const loadNotes = async () => {
      try {
        await store.dispatch('loadNotes', userId.value);
        // 初始化 folderOpen 状态
        folders.value.forEach(folder => {
          folderOpen.value[folder.id] = false;
        });
      } catch (error) {
        console.error('加载笔记失败:', error);
        ElMessage.error('加载笔记失败');
      }
    };

    // 加载用户信息
    const loadUserInfo = async () => {
      try {
        const userid = userId.value;
        const response = await axios.get('http://127.0.0.1:5000/load-userInfo', {
          params: { userid }
        });
        const userData = response.data[0];
        profileAvatar.value = userData.avatar_url || defaultAvatar;
        if (!userData) {
          console.log('未找到用户数据！');
          return;
        }
      } catch (error) {
        console.error('加载用户信息失败:', error);
        ElMessage.error('加载用户信息失败');
      }
    };

    const exportNote = async (noteId) => {
      // 获取选定笔记的内容
      const note = folders.value.flatMap(folder => folder.notes).find(note => note.id === noteId);
      if (note) {
        // 将HTML内容转换为docx库能够识别的内容
        const content = convertHtmlToContent(note.content);

        const doc = new Document({
          sections: [
            {
              properties: {},
              children: content,
            },
          ],
        });

        const blob = await Packer.toBlob(doc);
        saveAs(blob, `${note.name}.docx`);
      } else {
        ElMessage.error('找不到笔记内容');
      }
    };

    const convertHtmlToContent = (html) => {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");
      const elements = doc.body.childNodes;
      const content = [];
      elements.forEach((element) => {
        const paragraph = new Paragraph({
          children: parseElement(element),
        });
        content.push(paragraph);
      });
      return content;
    };

    const parseElement = (element) => {
   const children = [];
   element.childNodes.forEach((node) => {
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
       children.push(textRun);        }
   });
   return children;
 };

    onMounted(() => {
      loadNotes();
      loadUserInfo();
    });


    return {
      notes,
      folders,
      profileAvatar,
      userId,
      createDialogVisible,
      createFolderDialogVisible,
      createOptionsDialogVisible,
      newNote,
      newFolder,
      fileList,
      folderOpen,
      navigateToProfile,
      showCreateOptionsDialog,
      showCreateFolderDialog,
      showCreateDialog,
      createFolder,
      handleFileChange,
      uploadFile,
      handleCommand,
      handleFolderCommand, 
      openNoteDetail,
      toggleStar,
      toggleFolder,
      loadNotes,
      exportNote,
      isOpen,
      getIconComponent,
      FolderIcon,
    };
  }
};
</script>

<style scoped>
.menu {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.close-sidebar {
  cursor: pointer;
  margin-bottom: 20px;
  text-align: center;
  background-color: #fffffffa;
  padding: 10px;
  box-shadow: inset 2px 2px 4px #e6e6e6, inset -2px -2px 4px #e6e6e6;
  border: 3px solid #e6e6e6;
  border-radius: 5px;
}

.profile-pic-container {
  cursor: pointer;
}

.profile-pic[data-v-d9beb9c5] {
  width: 120px;
  height: 120px;
  margin-top: 15px;
  border-radius: 50%;
  transition: width 0.3s, height 0.3s;
}

.note-management {
  width: 100%;
  margin-top: 20px;
}

.new-note {
  cursor: pointer;
  margin-bottom: 20px;
  text-align: center;
  background-color: #fffffffa;
  padding: 10px;
}

.note-item{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #ffffffe6;
    padding: 10px;
    cursor: pointer;
    margin-bottom: 5px;
    /* box-shadow: inset 2px 2px 10px #e6e6e6, inset -2px -2px 10px #e6e6e6; */
    /* border: 2px solid #e6e6e6; */
    border-radius: 0px;
}

.note-title {
  display: flex;
  align-items: center;
}

.note-cover{
    width: 35px;
    height: 35px;
    border-radius: 2px;
    object-fit: cover;
    margin-right: 10px;
    margin-left: 2px;
}

.note-info {
  display: flex;
  flex-direction: column;
}

.note-name{
    font-weight: bold;
    font-size: 3%;
}

.note-date {
  font-size: 2%;
  color: #000;
}

.note-actions {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  cursor: pointer;
  color: #0e0e0f;
}

.el-icon-arrow-down {
  font-size: 12px;
}

.el-icon-star {
  cursor: pointer;
}

.folder-item {
  margin-bottom: 3px;
}

.folder-header{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #ffffff;
    padding: 10px;
    height: 50px;
    cursor: pointer;
}

.folder-icon{
    width: 25%;
    margin-right: 8px;
}

.folder-name {
  flex: 1; /* 文件夹名字占据剩余空间 */
  margin-right: 8px; /* 调整文件夹名字和下拉按钮之间的间距 */
  font-size: small;
}

.dropdown-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.folder-content {
  margin-top: 2%;
  padding-left: 6%;
}
</style>

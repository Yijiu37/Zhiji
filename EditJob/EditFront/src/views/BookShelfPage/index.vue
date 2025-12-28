<template>
  <div class="app-container">
    <div class="top-tool">
      <el-icon
        v-if="currentFolder !== null"
        class="back_button"
        @click="backToFolders"
        size="40px"
      >
        <Back />
      </el-icon>
      <span class="mybookshelf">我的文档</span>
      <div class="tool-icons">
      <el-icon class="addNew_button" @click="showCreateDialog" size="30px"><Plus /></el-icon>
      <el-icon class="addNew_button" @click="openChooseStyleDialog" size="30px"><Grid /></el-icon>
      </div>
      <img :src="profileAvatar" class="profile-pic" @click="gotoPersonalPage" />
    </div>
    <div v-if="currentFolder === null" :class="layout === 'grid' ? 'grid-container' : 'list-container'">
      <div v-for="folder in folders" :key="folder.id" :class="['folder', layout === 'grid' ? 'folder-grid' : 'folder-list']" 
      @click="loadNotes(folder.id)" @contextmenu.prevent="showContextMenu($event, folder)">
       <img :src="FolderIcon" alt="Folder Image" class="folder-image"/>
        <div :class="layout === 'grid' ? 'folderName-grid' : 'folderName-list'">{{ folder.folder_name }}</div>
      </div>
    </div>
    <div v-else :class="layout === 'grid' ? 'grid-container' : 'list-container'">
      <div v-for="note in currentFolder.notes" :key="note.id" :class="['folder', layout === 'grid' ? 'folder-grid' : 'folder-list']" @click="gotoEditNote(note.id)">
        <img :src="note.note_cover_url" alt="Note Image" class="folder-image"/>
        <div :class="['noteName', layout === 'grid' ? 'noteName-grid' : 'noteName-list']">{{ note.document_name }}</div>
        <div class="note-date">最新修改时间：{{ note.saved_time }}</div>
      </div>
    </div>
    <el-dialog class="el-dialog" v-model="dialogVisible" title="请选择文件夹的排列样式：">
      <div class="dialog-buttons">
        <el-button type="primary" @click="setGridLayout">网格排列</el-button>
        <el-button type="primary" @click="setListLayout">列表排列</el-button>
      </div>
    </el-dialog>

    <!-- 新建文件夹或笔记的对话框 -->
    <el-dialog class="el-dialog" v-model="createDialogVisible" title="创建:">
      <div class="dialog-buttons">
        <el-button type="primary" @click="createNewFolder">文件夹</el-button>
        <el-button type="primary" @click="openNewNoteDialog">笔记</el-button>
      </div>
    </el-dialog>

    <!--新建笔记对话框-->
    <el-dialog class="el-dialog" v-model="newNoteDialogVisible" title="新建笔记">
          <el-form :model="newNoteForm">
              <el-form-item label="笔记名称">
                  <el-input v-model="newNoteForm.document_name"></el-input>
              </el-form-item>
              <el-form-item label="选择封面">
                  <el-upload
                      class="upload-demo"
                      action="http://127.0.0.1:5000/upload"
                      :on-success="handleUploadSuccess"
                      :before-upload="beforeUpload"
                      :file-list="fileList">
                      <el-button slot="trigger" size="small" type="primary">选取文件</el-button>
                      <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过500kb</div>
                  </el-upload>
              </el-form-item>
          </el-form>
          <div slot="footer" class="dialog-footer">
              <el-button @click="newNoteDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="createNewNote">创建</el-button>
          </div>
      </el-dialog>
      <!--右键点击对文件夹的操作，现在还有bug-->
      <vue3-context-menu ref="menuRef" :options="showContextMenu" />

      <!-- 悬浮按钮 -->
  <el-button class="floating-button" type="primary" @click="openChooseTemplate">模板</el-button>

      <!-- 模板选择弹出框 -->
  <el-dialog class="el-dialog" v-model="chooseTemplateDialogVisible" title="选择模板">
    <div class="chooseTemplate-div">
      <!-- 这里放置你的模板选择内容 -->
      <div v-for="template in templates" :key="template.id" class="template-item">
          <img :src="template.is_builtin ? defaultTemplateAvatar : template.cover_url" alt="Template Image" class="template-image"/>
          <div>{{ template.name }}</div>
          <el-button @click="selectTemplate(template)">选择</el-button>
        </div>
    </div>
  </el-dialog>
  </div>
</template>


<script setup>
import { ref, onMounted, computed } from 'vue';
import 'element-plus/dist/index.css';
import { ElButton, ElDialog, ElMessageBox, ElMessage, ElUpload, ElForm, ElFormItem, ElInput } from 'element-plus';
import FolderIcon from '@/assets/images/folder.svg'; // 文件夹图标
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import axios from 'axios';
import { useEditorStore } from '@/store/index.ts';
import ContextMenu from '@imengyu/vue3-context-menu'
import defaultAvatar from '@/assets/images/touxiang.png';
import defaultTemplateAvatar from '@/assets/images/template_default.png';


const dialogVisible = ref(false);
const newNoteDialogVisible = ref(false);
const chooseTemplateDialogVisible = ref(false); // 模板选择弹出框的可见性
const createDialogVisible = ref(false); // 新建对话框的可见性
const layout = ref('grid');
const currentFolder = ref(null);
const router = useRouter();
//获得笔记和文件夹
const notes = computed(() => store.getters.getNotes);
const folders = computed(() => store.getters.getFolders);
const editorStore = useEditorStore();
const store = useStore();
const userId = editorStore.getUserId();
const newNoteForm = ref({
  document_name: '',
  note_cover_url: '',
  content: '',
});
const fileList = ref([]);
const menuRef = ref(null);
const templates = ref([]); // 模板列表
const profileAvatar = ref('');


onMounted(() => {
if (userId) {
  store.dispatch('loadNotes', userId)
    .then(() => {
      console.log('文件夹加载成功');
    })
    .catch((error) => {
      console.error('加载文件夹失败', error);
    });

    //加载用户数据
    loadUserInfo();
    // 加载模板数据
    loadTemplates();
}
});

  // 加载用户信息
  const loadUserInfo = async () => {
    try {
      const userid = userId;
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

  //加载模板信息
  const loadTemplates = async () => {
  try {
    // 获取内置模板
    const templateResponse = await axios.get('http://127.0.0.1:5000/templates');
    const builtInTemplates = templateResponse.data.templates.map(template => ({
      ...template,
      is_builtin: true
    }));

    // 获取用户自定义模板
    const userTemplatesResponse = await axios.get('http://127.0.0.1:5000/user_templates', {
      params: { user_id: userId }  // 传递用户ID
    });
    const userOwnTemplates = userTemplatesResponse.data.templates.map(template => ({
      ...template,
      is_builtin: false
    }));

    // 合并模板
    const loadedTemplates = [...builtInTemplates, ...userOwnTemplates];
    templates.value = loadedTemplates;
  } catch (error) {
    console.error('加载模板失败', error);
  }
};




const gotoPersonalPage = () => {
    router.push({ path: '/PersonalPage'});
  };

const openChooseStyleDialog = () => {
  dialogVisible.value = true;
};

const setGridLayout = () => {
  layout.value = 'grid';
dialogVisible.value = false;
};

const setListLayout = () => {
  layout.value = 'list';
  dialogVisible.value = false;
};

const loadNotes = (folderId) => {
const selectedFolder = folders.value.find(folder => folder.id === folderId);
if (selectedFolder) {
  currentFolder.value = selectedFolder;
}
};

const backToFolders = () => {
currentFolder.value = null;
};

const gotoEditNote = (noteId) => {
router.push({ path: `/Edit`, query: { user_id: userId, note_id: noteId } });
};

const openNewNoteDialog = () => {
if (currentFolder.value === null) {
  ElMessage.error('请先选择一个文件夹');
  return;
}
newNoteDialogVisible.value = true;
};

// 新建文件夹函数
const createNewFolder = () => {
ElMessageBox.prompt('请输入文件夹名称', '新建文件夹', {
  confirmButtonText: '确定',
  cancelButtonText: '取消',
}).then(({ value }) => {
  axios.post('http://127.0.0.1:5000/create-folder', {
    user_id: userId,
    folder_name: value,
  }).then(response => {
    ElMessage.success('文件夹创建成功');
    createDialogVisible.value = false;
    store.dispatch('loadNotes', userId); // 重新加载文件夹
  }).catch(error => {
    ElMessage.error('创建文件夹失败');
  });
}).catch(() => {
  ElMessage.info('取消创建文件夹');
});
};

// 新建笔记函数
const createNewNote = () => {
  createDialogVisible.value = false;
  if (!newNoteForm.value.document_name) {
    ElMessage.error('请填写笔记名称');
    return;
  }
  axios.post('http://127.0.0.1:5000/save-note', {
    user_id: userId,
    document_name: newNoteForm.value.document_name,
    note_cover_url: newNoteForm.value.note_cover_url,
    content: newNoteForm.value.content, // 添加模板内容字段
    saved_time: new Date().toLocaleString(),
    folder_id: currentFolder.value.id,
  }).then(response => {
    ElMessage.success('笔记创建成功');
    // 重新加载当前文件夹中的笔记
    store.dispatch('loadNotes', userId).then(() => {
      const selectedFolder = folders.value.find(folder => folder.id === currentFolder.value.id);
      if (selectedFolder) {
        currentFolder.value = selectedFolder;
      }
    });
    newNoteDialogVisible.value = false;
  }).catch(error => {
    ElMessage.error('创建笔记失败');
  });
};

const handleUploadSuccess = (response, file) => {
newNoteForm.value.note_cover_url = `http://127.0.0.1:5000/uploads/${response.filename}`;
};

const beforeUpload = (file) => {
const isJPG = file.type === 'image/jpeg' || file.type === 'image/png';
const isLt500k = file.size / 1024 / 1024 < 0.5;

if (!isJPG) {
  ElMessage.error('上传图片只能是 JPG/PNG 格式!');
}
if (!isLt500k) {
  ElMessage.error('上传图片大小不能超过 500KB!');
}
return isJPG && isLt500k;
};

// 定义右键菜单项
const contextMenuItems = [
{
  label: '删除文件夹',
  icon: 'el-icon-delete',
  action: (folder) => deleteFolder(folder.id)
},
{
  label: '修改文件夹信息',
  icon: 'el-icon-edit',
  action: (folder) => editFolder(folder)
}
];

// 显示右键菜单
const showContextMenu = (event, folder) => {
event.preventDefault();
console.log('folder:', folder);
if (menuRef.value) {
  ContextMenu.showContextMenu(
    contextMenuItems.map(item => ({
      ...item,
      action: () => item.action(folder) // 绑定 folder 参数
    })),
    { x: event.clientX, y: event.clientY }
  );
} else {
  console.error('menuRef is null');
}
};


//删除文件夹
const deleteFolder = (folderId) => {
ElMessageBox.confirm('确认删除此文件夹吗？', '警告', {
  confirmButtonText: '确定',
  cancelButtonText: '取消',
  type: 'warning',
}).then(() => {
  axios.post('http://127.0.0.1:5000/delete-folder', {
    folder_id: folderId
  }).then(response => {
    ElMessage.success('文件夹删除成功');
    store.dispatch('loadNotes', userId); // 重新加载文件夹
  }).catch(error => {
    ElMessage.error('删除文件夹失败');
  });
}).catch(() => {
  ElMessage.info('取消删除');
});
};

//编辑文件夹
const editFolder = (folder) => {
ElMessageBox.prompt('修改文件夹名称', '修改文件夹信息', {
  confirmButtonText: '确定',
  cancelButtonText: '取消',
  inputValue: folder.folder_name,
}).then(({ value }) => {
  axios.post('http://127.0.0.1:5000/update-folder', {
    folder_id: folder.id,
    folder_name: value,
  }).then(response => {
    ElMessage.success('文件夹信息修改成功');
    store.dispatch('loadNotes', userId); // 重新加载文件夹
  }).catch(error => {
    ElMessage.error('修改文件夹信息失败');
  });
}).catch(() => {
  ElMessage.info('取消修改');
});
};

// 打开选择模板悬浮框
const openChooseTemplate = () => {
chooseTemplateDialogVisible.value = true;
};

// 选择模板后创建一个新的笔记
const selectTemplate = (template) => {
  // 设置新笔记表单的内容为选定模板的内容
  if(currentFolder.value === null) {
    ElMessage.error('请先选择一个文件夹');
    return;
  }
  newNoteForm.value.document_name = template.name;
  newNoteForm.value.content = template.content;
  chooseTemplateDialogVisible.value = false;
  openNewNoteDialog(); // 打开新建笔记对话框
};

// 显示创建对话框
const showCreateDialog = () => {
  createDialogVisible.value = true;
};
</script>

<style scoped>  
.app-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background-color: aliceblue;
}

.addNew_button{
  cursor: pointer;
  margin: 0 10px;
}

.back_button{
  cursor: pointer;
  position: absolute;
  left: 5%;
}

.tool-icons{
  position: absolute;
  right:8%;
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin-right: 30px;
}

.profile-pic{
  position: absolute;
  right: 1%;
  width: 80px;
  height: 80px;
border-radius: 50%;
transition: width 0.3s, height 0.3s;
cursor: pointer;
}

.top-tool {
  display: flex;
  height: 7%;
  align-items: center;
  padding: 1rem;
  background-image: linear-gradient(160deg, #0b1c2e 10%, #4270b5 80%);
  color: white;
}

.top-tool button {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

.grid-container{
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem 1rem;
  padding: 3rem;
  overflow-y: auto;
}

.list-container {
flex: 1;
display: flex;
flex-direction: column;
gap: 1rem;
padding: 3rem;
overflow-y: auto;
}
.mybookshelf {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-weight: bold;
  font-size: 2rem;
}


.folder {
  display: flex;
  align-items: center;
  background-color: transparent;
  padding: 1rem;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer; 
}

.folder-grid {
  height: 150px;
  flex-direction: column;
  align-items: center; /* 垂直居中对齐 */
  justify-content: space-between; /* 水平空间在子元素间平均分配 */
  background-color: transparent;
  transition: transform 0.3s ease, background-color 0.3s ease; /* 添加平滑过渡效果 */
}

.folder-grid:hover {
  background-color: rgb(224, 237, 255);
  transform: translateY(-5px); 
}


.folder-list {
  flex-direction: row;
  align-items: center; /* 垂直居中对齐 */
  transition: transform 0.3s ease, background-color 0.3s ease; /* 添加平滑过渡效果 */
}

.folder-list:hover {
  background-color: rgb(224, 237, 255);
  transform: translateY(-5px);
}


.folder-image {
  width: 100px;
  height: auto;
  border-radius: 5px;
}

.folderName-grid {
  margin-top: 0.5rem;
  font-weight: bold;
}

.folderName-list
{
    margin-top: 0.5rem;
    font-weight: bold;
}

.noteName-grid{
  font-weight: bold;
}

.noteName-list{
  margin-left: 2rem;
  font-weight: bold;
}

.note-date{
  font-size: small;
  margin-left: auto;
}
.dialog-buttons {
margin-top: 1rem;
display: flex;
justify-content: space-around;
}


.floating-button {
position: fixed;
bottom: 10%;
right: 5%;
z-index: 1000;
width: 80px;
height: 80px;
border-radius: 50%;
display: flex;
align-items: center;
justify-content: center;
background-color: #002852;
color: white;
font-size: larger;
box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
cursor: pointer;
transition:transform 0.3s ease, background-color 0.3s;
}

.floating-button:hover {
background-color: #0057b4;
}

.template-container {
display: grid;
grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
gap: 1rem;
}

/*这里需要改到服务器 */
.chooseTemplate-div {
    display: flex;
    flex-wrap: wrap;
    gap: 10px; /* 可选：调整元素之间的间距 */
}

.template-item{
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 10px;
    padding: 10px;
    width: calc(33.33% - 10px);
    box-sizing: border-box;
    border: 2px solid gray;
}

.template-image {
  width: 160px;
    height: 120px;
    object-fit: cover; /* 确保图片按比例缩放并填充容器 */
}
/*到这里截止 */

.template-item div {
text-align: center;
margin-top: 0.5rem;
display: flex;
}

.el-button--primary {
    --el-button-text-color: var(--el-color-white);
    --el-button-bg-color: #1e4b7a;
    --el-button-border-color: #103155;
    --el-button-outline-color: #103155;
    --el-button-active-color: #103155;
    --el-button-hover-text-color: var(--el-color-white);
    --el-button-hover-link-text-color: var(--el-color-primary-light-5);
    --el-button-hover-bg-color: #003c79;
    --el-button-hover-border-color: var(--el-color-primary-light-3);
    --el-button-active-bg-color: var(--el-color-primary-dark-2);
    --el-button-active-border-color: var(--el-color-primary-dark-2);
    --el-button-disabled-text-color: var(--el-color-white);
    --el-button-disabled-bg-color: var(--el-color-primary-light-5);
    --el-button-disabled-border-color: var(--el-color-primary-light-5);
}

.el-dialog {
    --el-dialog-width: 20%;
    --el-dialog-margin-top: 25vh;
    --el-dialog-bg-color: var(--el-bg-color);
    --el-dialog-box-shadow: var(--el-box-shadow);
    --el-dialog-title-font-size: var(--el-font-size-large);
    --el-dialog-content-font-size: 14px;
    --el-dialog-font-line-height: var(--el-font-line-height-primary);
    --el-dialog-padding-primary: 16px;
    --el-dialog-border-radius: var(--el-border-radius-small);
    background: var(--el-dialog-bg-color);
    border-radius: var(--el-dialog-border-radius);
    box-shadow: var(--el-dialog-box-shadow);
    box-sizing: border-box;
    margin: var(--el-dialog-margin-top, 15vh) auto 50px;
    overflow-wrap: break-word;
    padding: var(--el-dialog-padding-primary);
    position: relative;
    width: var(--el-dialog-width, 50%);
}

</style>

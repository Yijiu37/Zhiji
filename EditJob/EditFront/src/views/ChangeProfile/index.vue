<template>
  <div class="edit-profile-page">
    <el-form :model="form" ref="form" label-width="100px">
      <!-- 头像 -->
      <el-form-item label="">
        <div class="avatar-container">
          <el-avatar :src="imageUrl" shape="circle" style="cursor: pointer; width: 150px; height: 150px; margin: 20px auto;" @click="openAvatarUploader" />
          <input ref="avatarInput" type="file" accept="image/*" @change="handleAvatarChange" style="display: none;" />
          <span class="upload-label" style="cursor: pointer;" @click="openAvatarUploader">修改头像</span>
        </div>
      </el-form-item>
      
      <!-- 用户名和密码输入框 -->
      <el-form-item label="用户名">
        <el-input v-model="username" style="width: 300px" placeholder="输入新的用户名" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="password" style="width: 300px" placeholder="输入新的密码" />
      </el-form-item>
      
      <!-- 保存按钮 -->
      <el-form-item>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRouter } from 'vue-router';
import { useEditorStore } from '@/store/index.ts';

export default {
  name: 'ChangePage',
  props: {
    initialImageUrl: {
      type: String,
      default: ''
    },
    userid: {
      type: String, 
      required: true
    }
  },
setup(props, { emit }) {
    const username = ref('');
    const password = ref('');
    const imageUrl = ref('');
    const editorStore = useEditorStore();
    const avatarFile = ref(null); // 存储上传的文件
    const router = useRouter();
    const userId = editorStore.getUserId(); // 登录的用户id


    
    // 提交修改的用户信息
    const submitForm = async () => {
      ElMessageBox.confirm('确认修改用户信息？', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }).then(async () => {
          if (!userId) {
        ElMessage.error('用户未登录');
        router.push('/');
        return;
      }
      const formData = new FormData();
      formData.append('id', userId);
      formData.append('username', username.value);
      formData.append('password', password.value);
      if (avatarFile.value) {
        formData.append('avatar', avatarFile.value);
      }

      try {
        const response = await saveProfileToDatabase(formData);
        if (response.status === 200) {
          ElMessage.success('用户信息已更新！');
          // 更新头像URL
          if (response.data.avatar_url) {
            imageUrl.value = response.data.avatar_url;
            emit('update-avatar', imageUrl.value); // 发送自定义事件到父组件，更新头像
          }
          // 其他操作，例如刷新页面
          location.reload(); // 示例：刷新页面
        } else {
          ElMessage.error('修改失败');
        }
      } catch (error) {
        ElMessage.error('修改失败');
      }
        }).catch(() => {
          ElMessage.info('已取消修改');
        });
        
      
    };

    const saveProfileToDatabase = async (profile) => {
      return axios.post('http://127.0.0.1:5000/updateProfile', profile);
    };

    const openAvatarUploader = () => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'image/*';
      input.onchange = handleAvatarChange;
      input.click();
    };

    const handleAvatarChange = (event) => {
      const file = event.target.files[0];
      const isLt2M = file.size / 1024 / 1024 < 2;

      if (!file.type.startsWith('image/')) {
        ElMessage.error('上传头像图片只能是图片格式!');
        return;
      }
      if (!isLt2M) {
        ElMessage.error('上传头像图片大小不能超过 2MB!');
        return;
      }

      avatarFile.value = file;
      const reader = new FileReader();
      reader.onload = () => {
        imageUrl.value = reader.result;
      };
      reader.readAsDataURL(file);
    };

    return {
      username,
      password,
      imageUrl,
      submitForm,
      openAvatarUploader,
      handleAvatarChange
    };
  }
};
</script>

<style scoped>
.edit-profile-page{
    background-color: aliceblue;
    height: 100%;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
}
.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
}
.el-form {
  width: 300px;
  margin-top: 20px;
}
.avatar-container {
  position: relative;
  text-align: center;
}
.upload-label {
  font-size: 12px;
  color: #409eff;
}
</style>

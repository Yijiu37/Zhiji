<template>
  <div class="personal-page">
    <div class="profile-page">
      <!-- Top navigation and user profile -->
      <div class="profile-header">
        <div class="profile-avatar">
          <img :src="avatarUrl" class="profile-avatar-img">
        </div>
        <div class="profile-user">
          <div class="profile-user-header">
            <div class="profile-user-title">
                <span class="username">用户名：{{ username }}</span>
                <span class="user-id">用户ID：{{ userId }}</span>
              <!-- Level icon -->
            </div>
            <div class="profile-header-buttons">
              <div class="profile-edit-profile-button">
                <button @click="goBack">返回</button>
              </div>
              <!-- Additional buttons or controls -->
            </div>
          </div>
        </div>
      </div>

      <div class="profile-main">
        <!-- 左侧菜单 -->
        <div class="profile-sidebar">
          <header class="profile-sidebar-header">个人中心</header>
          <ul class="profile-sidebar-list">
            <li v-for="(item, index) in menus" :key="index" @click="selMenu(item)">
              <a :class="'profile-menu-item ' + (activeIndex === item.way ? 'active' : '')">
                <i :class="item.icon" style="font-size: 1.125rem; margin-right: 0.625rem;"></i>
                <span>{{ item.name }}</span>
              </a>
            </li>
          </ul>
        </div>

        <!-- Right side content -->
        <div class="profile-content">
          <component :is="currentComponent" @update-avatar="updateAvatarUrl" :userid=userId></component>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted,watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useStore } from 'vuex'
import { useEditorStore } from '@/store'
import { ElMessage, ElMessageBox } from 'element-plus'; // 添加了ElMessageBox显示提示
import CollectionPage from '../CollectionPage/index.vue';
import ChangePage from '../ChangeProfile/index.vue';
import CInvitationPage from '../CInvitationPage/index.vue';
import axios from 'axios'
import defaultAvatar from '@/assets/images/touxiang.png';

export default {
  name: 'UserProfilePage',
  components: {
    CollectionPage,
    ChangePage,
    CInvitationPage,
  },
  setup() {
      const editorStore = useEditorStore();
      const router = useRouter();
      const store = useStore()
      const route = useRoute();
      const userId = editorStore.getUserId();
      const username = ref('默认用户');
      const avatarUrl = ref(''); // 用于显示头像的URL
    
    const activeIndex = ref('ChangePage'); // 默认显示修改个人信息页面
    const menus = [
      { name: '修改个人信息', way: 'ChangePage' },
      { name: '我的消息', way: 'CInvitationPage' },
      { name: '我的收藏', way: 'CollectionPage' },
      { name: '退出登录', way: 'exit' },
      { name: '注销账户', way: 'deleteAccount' },
    ];


    onMounted(async () => {
      try {
        console.log(userId);
        // 从数据库获取用户名
        const fetchedUsername = await fetchUsernameFromDatabase(userId);
        if (fetchedUsername) {
          username.value = fetchedUsername.username;
          // 获取头像URL
          if(!fetchedUsername.avatar_url){
            avatarUrl.value = defaultAvatar
          }else{
            avatarUrl.value = fetchedUsername.avatar_url;
          }
        } else {
          username.value = '默认用户'; // 默认用户名
        }
      } catch (error) {
        username.value = '默认用户';
      }
    });

   

      //根据用户id获取用户信息
      const fetchUsernameFromDatabase = async (userid) => {
          if (!userid) {
              console.log('未找到该用户！');
              return;
          }
          try {
              const response = await axios.get('http://127.0.0.1:5000/load-userInfo', {
                  params: { userid }
              });
              const userData = response.data[0];
              if (!userData) {
                  console.log('未找到用户数据！');
                  return;
              }
              return userData;
          } catch (error) {
              console.error('获取用户数据时出错:', error);
          }
      };

      const currentComponent = computed(() => {
      switch (activeIndex.value) {
        case 'CollectionPage':
          return CollectionPage;
        case 'ChangePage':
          return ChangePage;
        case 'CInvitationPage':
          return CInvitationPage;
        default:
          return null; // 默认不加载任何组件
      }
    });

    const selMenu = async (item) => {
      activeIndex.value = item.way;
      if (item.way === 'deleteAccount') {
        ElMessageBox.confirm('此操作将永久删除您的账户和所有笔记, 是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }).then(async () => {
          await deleteAccount(userId);
        }).catch(() => {
          ElMessage.info('已取消删除');
        });
      } else if (item.way === 'exit') {
        ElMessageBox.confirm('您确定要退出登录吗?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }).then(() => {
          router.push({ path: '/' });
          ElMessage.success('已退出登录');
        }).catch(() => {
          ElMessage.info('已取消退出');
        });
      }
    };


    const goBack = () => {
      router.go(-1);
    };
    
    const updateAvatarUrl = (newAvatarUrl) => {
      if(!avatarUrl.value){
        avatarUrl.value = defaultAvatar
      }else{
        avatarUrl.value = newAvatarUrl; // 更新头像URL
      }
    };

    const deleteAccount = async (userid) => {
  try {
    const response = await axios.delete('http://127.0.0.1:5000/delete-user', {
      data: { userid }
    });
    if (response.status === 200) {
      ElMessage.success('账户已成功注销');
      router.push({ path: '/' });
    } else {
      ElMessage.error('注销账户失败');
    }
  } catch (error) {
    console.error('注销账户时出错:', error);
    ElMessage.error('注销账户时发生错误');
  }
};


    return {
      goBack,
      username,
      userId,
      activeIndex,
      menus,
      selMenu,
      currentComponent,
      updateAvatarUrl,
      avatarUrl, // 返回 avatarUrl 以便在模板中访问
    };
  },
};
</script>

<style scoped>
.personal-page{
    width: 100%;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #f3f3f3;
}

.profile-page {
  width: 80%;
  height: 80vh; /* 设置页面高度占视口高度的90% */
  background: #ffffff;
  border-radius: 0.9375rem; /* 调整为大一点的圆角 */
  box-shadow: 0 0.25rem 1rem rgba(0, 0, 0, 0.1); /* 调整阴影效果 */
  display: flex;
  flex-direction: column;
  padding: 1.875rem; /* 调整为大一点的内边距 */
}

.profile-main {
  flex-grow: 1;
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-top: 1.25rem; /* 20px / 16 */
  height: calc(100% - 1.25rem - 140px); /* 减去margin-top和header的高度 */
}


.profile-header {
  width: 100%;
  display: flex;
  margin-bottom: 1.25rem; /* 20px / 16 */
  box-shadow: 0 0.125rem 0.5rem rgba(0, 0, 0, 0.1); /* 0 2px 8px */
  border-radius: 0.625rem; /* 10px / 16 */
  background: #ffffff;
  flex: 10%;
}

.profile-avatar {
  margin-right: 1.5rem; /* 24px / 16 */
  flex-shrink: 0;
}

.profile-avatar-img{
    width: 6rem;
    height: 6rem;
    border-radius: 50%;
    border: 0.0625rem solid #ebebeb;
}

.profile-user {
  flex-grow: 1;
}

.profile-user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-user-title {
  margin-top: 0.8rem;
  height: 100%;
  width: 80%;
  display: flex;
  align-items: left;
  flex-direction: column;
}

.username,
.user-id {
  margin: 5px 0;
  font-size: 1rem; /* 16px / 16 */
  font-weight: 600;
}

.profile-header-buttons {
  display: flex;
}

.profile-edit-profile-button {
  margin-right: 0.625rem; /* 10px / 16 */
}

.profile-user-audit {
  display: flex;
  align-items: center;
}

.profile-user-id {
  font-size: 0.75rem; /* 12px / 16 */
  color: #ccc;
}

.profile-user-intro {
  margin-top: 0.75rem; /* 12px / 16 */
  color: #666;
  line-height: 1.125rem; /* 18px / 16 */
}

.profile-icon {
  font-size: 1.125rem; /* 18px / 16 */
  margin-right: 0.625rem; /* 10px / 16 */
}


.profile-sidebar {
  width: 10.5rem; /* 280px / 16 */
  margin-right: 1.25rem; /* 20px / 16 */
  padding: 1.25rem; /* 20px / 16 */
  background: #ffffff;
  border-radius: 0.625rem; /* 10px / 16 */
  box-shadow: 0 0.125rem 0.5rem rgba(0, 0, 0, 0.1); /* 0 2px 8px */
}

.profile-sidebar-header {
  padding: 0.625rem 1.25rem; /* 10px 20px / 16 */
  border-bottom: 0.0625rem solid #ebebeb; /* 1px / 16 */
  font-size: 1rem; /* 16px / 16 */
}

.profile-sidebar-list {
  padding: 0.625rem 0; /* 10px / 16 */
}

.profile-menu-item {
  padding: 0.625rem 1.25rem; /* 10px 20px / 16 */
  font-size: 0.875rem; /* 14px / 16 */
  color: #666;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.profile-menu-item.active {
  color: #00c3ff;
}

.profile-content {
  flex-grow: 1;
  max-height: 100%; /* 确保不超过父容器高度 */
  background: aliceblue;
  border-radius: 0.625rem; /* 10px / 16 */
  box-shadow: 0 0.125rem 0.5rem rgba(0, 0, 0, 0.1); /* 0 2px 8px */
  overflow-y: auto; /* 启用垂直滚动条 */
}
</style>

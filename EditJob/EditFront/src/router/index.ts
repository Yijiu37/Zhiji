import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

// createRouter 创建路由实例，===> new VueRouter()
// history 是路由模式，hash模式，history模式
// createWebHistory() 是开启history模块 
// createWebHashHistory() 是开启hash模式   

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomePage/index.vue')
  },
  {
    path: '/Edit',
    name: 'Edit',
    component: () => import('../views/Edit/index.vue')
  },
  {
    path: '/PersonalPage',
    name: 'PersonalPage',
    component: () => import('../views/PersonalPage/index.vue')
  },
  {
    path: '/CollectionPage',
    name: 'CollectionPage',
    component: () => import('../views/CollectionPage/index.vue')
  },
  {
    path: '/ChangeProfile',
    name: 'ChangeProfile',
    component: () => import('../views/ChangeProfile/index.vue')
  },
  {
    path: '/BookShelfPage',
    name: 'BookShelfPage',
    component: () => import('../views/BookShelfPage/index.vue')
  }
] as RouteRecordRaw[]
const router = createRouter({
  history: createWebHistory(),
  routes: routes
})


export default router
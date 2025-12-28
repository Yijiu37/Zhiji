<template>
  <div v-if="loginModel === '注册'" class="container a-container" id="a-container">
      <form class="form" id="a-form" @submit.prevent="register">
          <h2 class="form_title title">注册新的账户</h2>
          <div class="form__icons">
              <img class="form__icon" src=" " />
              <img class="form__icon" src=" " />
              <img class="form__icon" src=" " />
          </div>
          <input class="form__input" type="text" placeholder="用户名" v-model="registerForm.username" />
          <input class="form__input" type="password" placeholder="密码" v-model="registerForm.password" />
          <div class="login-info">
              <a class="form__link" @click="forgetPassword">忘记密码了？</a>
              &nbsp;&nbsp;&nbsp;&nbsp;
              <a class="form__link" @click="switchModel('登录')">使用账号登录</a>
          </div>
          <button class="form__button button submit" type="submit">注&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;册</button>
      </form>
  </div>

  <div v-else-if="loginModel === '登录'" class="container b-container" id="b-container">
      <form class="form" id="b-form" @submit.prevent="login">
          <h2 class="form_title title">Welcome to KnowNote! </h2>
          <h3 class="slogan">知记，你的智慧知己！ </h3>
          <div class="form__icons">
              <img class="form__icon" src=" " />
              <img class="form__icon" src=" " />
              <img class="form__icon" src=" " />
          </div>
          <input class="form__input" type="text" placeholder="用户名" v-model="loginForm.username" />
          <input class="form__input" type="password" placeholder="密码" v-model="loginForm.password" />
          <div class="login-info">
              <a class="form__link" @click="forgetPassword">忘记密码了？</a>
              &nbsp;&nbsp;&nbsp;&nbsp;
              <a class="form__link" @click="switchModel('注册')">注册新账户</a>
          </div>
          <button class="form__button button submit" type="submit">登&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;录</button>
      </form>
  </div>

  <div v-else class="container">
      <editor-content :editor="editor" />
  </div>

</template>

<script setup lang="ts">
import { defineComponent, onMounted, onBeforeUnmount, ref } from 'vue';
import { useRouter } from 'vue-router';
import { Editor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import { ElMessage } from 'element-plus';
import axios from 'axios';
import { useEditorStore } from '@/store/index.ts';

// 忘记密码提示
const forgetPassword = () => {
ElMessage({
  message: '那我们也没有办法！自求多福吧！',
  type: 'success',
})
}

// 模式：登录，token，注册
let loginModel = ref('登录')

const switchModel = (model: string) => {
  loginModel.value = model
}

const editor = ref<Editor | null>(null)
const router = useRouter()
const editorStore = useEditorStore();

const registerForm = ref({
username: '',
password: '',
})

const loginForm = ref({
username: '',
password: '',
})



onMounted(() => {
editor.value = new Editor({
  extensions: [StarterKit],
})
})

onBeforeUnmount(() => {
editor.value?.destroy()
})

const register = async () => {
try {
  const response = await axios.post('http://127.0.0.1:5000/register', registerForm.value) //用户信息存入数据库
  ElMessage.success(response.data.message)
  switchModel('登录')
} catch (error) {
  ElMessage.error('注册失败！该用户名已存在！')
}
}

const login = async () => {
try {
  const response = await axios.post('http://127.0.0.1:5000/login', loginForm.value)
  const userId = response.data.user_id // 获取从后端返回的用户ID
  editorStore.setUserId(userId); // 使用 Pinia store 设置用户ID
  ElMessage.success(response.data.message)
  router.push({ path: '/BookShelfPage'});
} catch (error) {
  console.log('未找到用户信息！')
  ElMessage.error('登录失败')
}
}

</script>

<style scoped> 
.login-info {
  margin-top: 10px;
}
*, *::after, *::before {
margin: 0;
padding: 0;
box-sizing: border-box;
user-select: none;
}




.form {
display: flex;
justify-content: center;
align-items: center;
flex-direction: column;
width: 100%;
height: 100%;
}
.form__icon {
object-fit: contain;
width: 30px;
margin: 0 5px;
opacity: 0.5;
transition: 0.15s;
}
.form__icon:hover {
opacity: 1;
transition: 0.15s;
cursor: pointer;
}
.form__input{
    width: 350px;
    height: 40px;
    margin: 4px 0;
    padding-left: 16px;
    font-size: 13px;
    letter-spacing: 0.15px;
    border: none;
    outline: none;
    color: black;
    font-family: "Montserrat", sans-serif;
    background-color: #ffffff;
    transition: 0.25s ease;
    border-radius: 8px;
    box-shadow: inset 2px 2px 4px #9696964d, inset -2px -2px 4px #011f3b59;
}
.form__input:focus {
    box-shadow: inset 4px 4px 4px #949494, inset -4px -4px 4px #ffffff;
}
.form__span {
margin-top: 30px;
margin-bottom: 12px;
}
.form__link{
    font-size: 15px;
    margin-top: 25px;
    border-bottom: 1px solid #a0a5a8;
    line-height: 2;
    cursor: pointer;
    text-decoration: none;
    color: rgb(255, 255, 255);
}

.form__link:hover{
    color: rgb(0, 26, 48);
}


.title {
font-size: 34px;
font-weight: 700;
line-height: 3;
font-family: fantasy;
color: var(--text-color);
}

.description {
font-size: 14px;
letter-spacing: 0.25px;
text-align: center;
line-height: 1.6;
}

.button{
    width: 180px;
    height: 50px;
    border-radius: 25px;
    margin-top: 30px;
    font-weight: 700;
    font-size: 16px;
    letter-spacing: 1.15px;
    background-color: white;
    color: #000000;
    border: none;
    outline: none;
    box-shadow: inset 2px 2px 2px #acacac, inset -2px -2px 4px #d1d1d1;
}

.righttools {
    background-color: #ebebeb;
    height: 100%;
    /* flex: 34%; */
    width: 30%;
    /* flex: 34%; */
    resize: horizontal;
    position: relative;
}

.lefttools {
    background-color: #ebebeb;
    height: 100%;
    width: 100%;
}

/**/
.a-container {
z-index: 100;
}

.b-container {
z-index: 0;
}

.switch {
display: flex;
justify-content: center;
align-items: center;
position: absolute;
top: 0;
left: 0;
height: 100%;
width: 400px;
padding: 50px;
z-index: 200;
transition: 1.25s;
background-color: #ecf0f3;
overflow: hidden;
box-shadow: 4px 4px 10px #d1d9e6, -4px -4px 10px #f9f9f9;
}
.switch__circle {
position: absolute;
width: 500px;
height: 500px;
border-radius: 50%;
background-color: #ecf0f3;
box-shadow: inset 8px 8px 12px #d1d9e6, inset -8px -8px 12px #f9f9f9;
bottom: -60%;
left: -60%;
transition: 1.25s;
}
.switch__circle--t {
top: -30%;
left: 60%;
width: 300px;
height: 300px;
}
.switch__container {
display: flex;
justify-content: center;
align-items: center;
flex-direction: column;
position: absolute;
width: 400px;
padding: 50px 55px;
transition: 1.25s;
}
.switch__button {
cursor: pointer;
}
.switch__button:hover {
box-shadow: 6px 6px 10px #d1d9e6, -6px -6px 10px #f9f9f9;
transform: scale(0.985);
transition: 0.25s;
}
.switch__button:active, .switch__button:focus {
box-shadow: 2px 2px 6px #d1d9e6, -2px -2px 6px #f9f9f9;
transform: scale(0.97);
transition: 0.25s;
}

.note-item[data-v-d9beb9c5] {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    background-color: #ffffff94;
    padding: 10px;
    border: 1px solid #ededed;
    border-radius: 5px;
    cursor: pointer;
}

/**/
.is-txr {
left: calc(100% - 400px );
transition: 1.25s;
transform-origin: left;
}

.is-txl {
left: 0;
transition: 1.25s;
transform-origin: right;
}

.is-z200 {
z-index: 200;
transition: 1.25s;
}

.is-hidden {
visibility: hidden;
opacity: 0;
position: absolute;
transition: 1.25s;
}

.is-gx {
animation: is-gx 1.25s;
}

@keyframes is-gx {
0%, 10%, 100% {
  width: 400px;
}
30%, 50% {
  width: 500px;
}
}

.container{
    width: 720px;
    height: 480px;
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    border-radius: 38px;
    backdrop-filter: blur(3px);
    background-color: rgba(26,198,255, 0.033);
    box-shadow: rgba(0, 0, 0, 0.3) 2px 8px 8px;
    border: 1px rgba(255,255,255,0.4) solid;
    border-bottom: 1px rgba(40,40,40,0.35) solid;
    border-right: 1px rgba(40,40,40,0.35) solid;
}
</style>

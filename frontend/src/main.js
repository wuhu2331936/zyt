import { createApp } from 'vue'
import { createPinia } from 'pinia'

// 全量引入兜底：保证 <van-xxx> 标签一定能解析到组件
import Vant from 'vant'
import {
  Button,
  Cell,
  CellGroup,
  Field,
  Form,
  NavBar,
  Tabbar,
  TabbarItem,
  Toast,
  Dialog,
  Notify,
  Loading,
  Uploader,
  ActionSheet,
  Popup,
  Picker,
  Card,
  Tag,
  Icon,
  Image as VanImage,
  Search,
  Empty,
  Switch,
  List,
  PullRefresh,
  Swipe,
  SwipeItem,
  FloatingBubble,
  Divider,
} from 'vant'
import 'vant/lib/index.css'

import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)

// 注册 Vant 组件
const vantComponents = {
  Button,
  Cell,
  CellGroup,
  Field,
  Form,
  NavBar,
  Tabbar,
  TabbarItem,
  Toast,
  Dialog,
  Notify,
  Loading,
  Uploader,
  ActionSheet,
  Popup,
  Picker,
  Card,
  Tag,
  Icon,
  VanImage,
  Search,
  Empty,
  Switch,
  List,
  PullRefresh,
  Swipe,
  SwipeItem,
  FloatingBubble,
  Divider,
}
// 模板里用的是 <van-button> / <van-nav-bar> 这类 kebab-case 标签，
// 必须注册成 "van-xxx" 才能被 Vue 解析，否则会渲染成无样式的裸标签。
const kebab = (s) => s.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase()
Object.entries(vantComponents).forEach(([name, comp]) => {
  app.component(name, comp)
  const k = kebab(name)
  app.component(k.startsWith('van-') ? k : `van-${k}`, comp)
})

// 全量注册，兜底覆盖模板中出现的任意 Vant 组件
app.use(Vant)

app.use(createPinia())
app.use(router)
app.mount('#app')
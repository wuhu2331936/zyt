import { createApp } from 'vue'
import { createPinia } from 'pinia'

// Vant 按需引入（已注释全量引入，如需简化可启用）
// import Vant from 'vant'
// import 'vant/lib/index.css'
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
Object.entries(vantComponents).forEach(([name, comp]) => {
  app.component(name, comp)
})

app.use(createPinia())
app.use(router)
app.mount('#app')
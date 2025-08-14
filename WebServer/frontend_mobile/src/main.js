import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

// 引入全局样式
import './styles/base.css'

// 引入Vant组件
import 'vant/lib/index.css'
import { 
  Tabbar, TabbarItem, NavBar, Button, 
  Slider, Field, Switch, Card, Cell, 
  CellGroup, Toast, Dialog, Image as VanImage 
} from 'vant'

const pinia = createPinia()
const app = createApp(App)

// 使用插件
app.use(router)
app.use(pinia)

// 注册Vant组件
app.use(Tabbar)
  .use(TabbarItem)
  .use(NavBar)
  .use(Button)
  .use(Slider)
  .use(Field)
  .use(Switch)
  .use(Card)
  .use(Cell)
  .use(CellGroup)
  .use(Toast)
  .use(Dialog)
  .use(VanImage)

app.mount('#app')
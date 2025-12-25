/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  // 将所有的泛型参数都设为 object，彻底解决 {} 和 any 的报错
  const component: DefineComponent<object, object, object>
  export default component
}

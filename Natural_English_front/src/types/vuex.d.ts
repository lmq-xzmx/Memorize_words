declare module 'vuex' {
  export * from 'vuex/types/index.d.ts'
}

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $store: import('vuex').Store<any>
  }
}
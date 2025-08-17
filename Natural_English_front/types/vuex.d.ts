// Vuex 类型声明文件
declare module 'vuex' {
  import { App, InjectionKey } from 'vue'
  
  export interface Store<S = any> {
    readonly state: S
    readonly getters: any
    dispatch: Dispatch
    commit: Commit
    subscribe<P extends MutationPayload>(fn: (mutation: P, state: S) => any): () => void
    subscribeAction<P extends ActionPayload>(fn: SubscribeActionOptions<P, S>): () => void
    watch<T>(fn: (state: S, getters: any) => T, cb: (value: T, oldValue: T) => void, options?: WatchOptions): () => void
    replaceState(state: S): void
    registerModule<T>(path: string, module: Module<T, S>, options?: ModuleOptions): void
    registerModule<T>(path: string[], module: Module<T, S>, options?: ModuleOptions): void
    unregisterModule(path: string): void
    unregisterModule(path: string[]): void
    hasModule(path: string): boolean
    hasModule(path: string[]): boolean
    hotUpdate(options: {
      actions?: ActionTree<S, S>
      mutations?: MutationTree<S>
      getters?: GetterTree<S, S>
      modules?: ModuleTree<S>
    }): void
  }
  
  export interface ActionContext<S, R> {
    dispatch: Dispatch
    commit: Commit
    state: S
    getters: any
    rootState: R
    rootGetters: any
  }
  
  export interface Dispatch {
    (type: string, payload?: any, options?: DispatchOptions): Promise<any>
    <P extends Payload>(payloadWithType: P, options?: DispatchOptions): Promise<any>
  }
  
  export interface Commit {
    (type: string, payload?: any, options?: CommitOptions): void
    <P extends Payload>(payloadWithType: P, options?: CommitOptions): void
  }
  
  export interface ActionTree<S, R> {
    [key: string]: Action<S, R>
  }
  
  export interface Action<S, R> {
    (this: Store<R>, injectee: ActionContext<S, R>, payload?: any): any
  }
  
  export interface MutationTree<S> {
    [key: string]: Mutation<S>
  }
  
  export interface Mutation<S> {
    (state: S, payload?: any): any
  }
  
  export interface GetterTree<S, R> {
    [key: string]: Getter<S, R>
  }
  
  export interface Getter<S, R> {
    (state: S, getters: any, rootState: R, rootGetters: any): any
  }
  
  export interface Module<S, R> {
    namespaced?: boolean
    state?: S | (() => S)
    getters?: GetterTree<S, R>
    actions?: ActionTree<S, R>
    mutations?: MutationTree<S>
    modules?: ModuleTree<R>
  }
  
  export interface ModuleTree<R> {
    [key: string]: Module<any, R>
  }
  
  export interface StoreOptions<S> {
    state?: S | (() => S)
    getters?: GetterTree<S, S>
    actions?: ActionTree<S, S>
    mutations?: MutationTree<S>
    modules?: ModuleTree<S>
    plugins?: Plugin<S>[]
    strict?: boolean
    devtools?: boolean
  }
  
  export interface Plugin<S> {
    (store: Store<S>): any
  }
  
  export interface MutationPayload {
    type: string
    payload: any
  }
  
  export interface ActionPayload {
    type: string
    payload: any
  }
  
  export interface SubscribeActionOptions<P, S> {
    before?: (action: P, state: S) => void
    after?: (action: P, state: S) => void
    error?: (action: P, state: S, error: Error) => void
  }
  
  export interface WatchOptions {
    deep?: boolean
    immediate?: boolean
  }
  
  export interface DispatchOptions {
    root?: boolean
  }
  
  export interface CommitOptions {
    silent?: boolean
    root?: boolean
  }
  
  export interface ModuleOptions {
    preserveState?: boolean
  }
  
  export interface Payload {
    type: string
  }
  
  export function createStore<S>(options: StoreOptions<S>): Store<S>
  export function useStore<S = any>(key?: InjectionKey<Store<S>> | string): Store<S>
  
  export const storeKey: string | InjectionKey<Store<any>>
}
<template>
  <div>
    <van-nav-bar title="家长监护" style="background:#673AB7;color:#fff;" />
    <div style="padding:12px">
      <div style="background:#fff;padding:8px;border-radius:10px;margin-bottom:12px">
        <div>实时画面</div>
        <img :src="videoUrl" style="width:100%;border-radius:8px;margin-top:8px" />
      </div>
      <div style="background:#fff;padding:8px;border-radius:10px">
        <div>实时消息</div>
        <div v-for="m in messages" :key="m.timestamp" style="padding:6px;border-bottom:1px solid #eee">{{m.timestamp}} - {{m.text}}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name:'Monitor',
  data(){
    return { videoUrl: '/api/video', messages: [] }
  },
  mounted(){
    // WebSocket 订阅实时消息示例
    const ws = new WebSocket(`${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/realtime`)
    ws.onmessage = (e)=>{
      try{
        const d = JSON.parse(e.data)
        this.messages.unshift({timestamp: new Date(d.timestamp*1000).toLocaleTimeString(), text: JSON.stringify(d)})
        if(this.messages.length>20) this.messages.pop()
      }catch(err){console.error(err)}
    }
  }
}
</script>
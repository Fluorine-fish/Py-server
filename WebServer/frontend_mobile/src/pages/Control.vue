<template>
  <div>
    <van-nav-bar title="远程控制" style="background:#009688;color:#fff;" />
    <div style="padding:12px">
      <div style="background:#fff;padding:12px;border-radius:10px;margin-bottom:12px">
        <div>亮度</div>
        <van-slider v-model="brightness" :min="0" :max="100" />
        <div style="margin-top:10px">色温</div>
        <van-slider v-model="kelvin" :min="2700" :max="6500" />
        <div style="margin-top:12px">
          <van-switch v-model="eyeMode" /> 护眼模式
        </div>
        <div style="margin-top:12px"><van-button type="primary" @click="apply">应用到台灯</van-button></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name:'Control',
  data(){return {brightness:80, kelvin:4000, eyeMode:true}},
  methods:{
    apply(){
      // 调用后端控制 API（示例）
      fetch('/api/control', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({brightness:this.brightness, kelvin:this.kelvin, eyeMode:this.eyeMode})})
        .then(r=>r.json()).then(j=>alert('已应用'))
    }
  }
}
</script>
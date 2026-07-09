<script setup lang="ts">
defineProps<{
  phone: string
  zalo: string
  messenger: string
}>()
</script>

<template>
  <section class="profile-section">
    <p class="profile-section__label">Liên hệ</p>
    <div class="profile-contact-grid">
      <a v-if="phone" class="profile-contact-item" :href="`tel:${phone}`">
        <p class="profile-contact-item__label">Điện thoại</p>
        <p class="profile-contact-item__value">{{ phone }}</p>
      </a>
      <div v-if="zalo" class="profile-contact-item">
        <p class="profile-contact-item__label">Zalo</p>
        <p class="profile-contact-item__value">{{ zalo }}</p>
      </div>
      <div v-if="messenger" class="profile-contact-item">
        <p class="profile-contact-item__label">Messenger</p>
        <p class="profile-contact-item__value">{{ messenger }}</p>
      </div>
    </div>
  </section>
</template>

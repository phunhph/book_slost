<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import KolCard from "@/components/kols/KolCard.vue";
import { kolWorkspaceUrl } from "@/lib/appUrls";
import { getErrorMessage } from "@/lib/errors";
import { getPublicKols } from "@/services/public";
import { useAuthStore } from "@/stores/auth";
import { useToastStore } from "@/stores/toast";
import type { KolPublicCard } from "@/types/profile";

const authStore = useAuthStore();
const toast = useToastStore();
const kols = ref<KolPublicCard[]>([]);
const isLoading = ref(true);
const loadFailed = ref(false);
const loadError = ref("");
const query = ref("");
const page = ref(1);
const pageSize = 9;

const featuredKols = computed(() => kols.value.filter((item) => item.username));
const isKolAccount = computed(() => authStore.user?.role === "kol");

const filteredKols = computed(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) return featuredKols.value;
  return featuredKols.value.filter((item) => {
    const haystack = [item.display_name, item.username, item.bio]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    return haystack.includes(q);
  });
});

const totalPages = computed(() => Math.max(1, Math.ceil(filteredKols.value.length / pageSize)));
const pagedKols = computed(() => {
  const start = (page.value - 1) * pageSize;
  return filteredKols.value.slice(start, start + pageSize);
});
const rangeStart = computed(() =>
  filteredKols.value.length === 0 ? 0 : (page.value - 1) * pageSize + 1,
);
const rangeEnd = computed(() => Math.min(page.value * pageSize, filteredKols.value.length));

watch(query, () => {
  page.value = 1;
});

watch(filteredKols, () => {
  if (page.value > totalPages.value) page.value = totalPages.value;
});

onMounted(async () => {
  try {
    kols.value = await getPublicKols();
  } catch (error) {
    loadFailed.value = true;
    loadError.value = getErrorMessage(error, "Không tải được danh sách creator.");
    toast.error(loadError.value);
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <section class="page-container py-10 sm:py-16 lg:py-16">
    <div
      v-if="isKolAccount"
      class="mb-8 rounded-[2rem] border border-fuchsia-400/20 bg-fuchsia-500/10 p-5 text-fuchsia-50"
    >
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p class="text-sm font-semibold uppercase tracking-[0.28em] text-fuchsia-200">Tài khoản KOL</p>
          <h2 class="mt-2 text-xl font-semibold text-white">Bạn đang đăng nhập bằng tài khoản creator/KOL</h2>
          <p class="mt-2 text-sm leading-6 text-fuchsia-100/90">
            Trang công khai này chỉ để xem marketplace. Để quản lý cá nhân và tùy chỉnh hồ sơ, hãy mở không gian KOL.
          </p>
        </div>
        <a
          :href="kolWorkspaceUrl('/dashboard', authStore.accessToken)"
          class="inline-flex items-center justify-center rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
        >
          Mở không gian KOL
        </a>
      </div>
    </div>

    <div class="grid gap-12 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.32em] text-sky-300">Marketplace công khai</p>
        <h1 class="mt-5 max-w-3xl text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
          Tìm KOL có phong cách rõ nét và luồng đặt lịch tối ưu cho di động.
        </h1>
        <p class="mt-6 max-w-2xl text-base leading-8 text-slate-300 sm:text-lg">
          Duyệt trang creator công khai, xem theme hồ sơ tùy chỉnh và gửi yêu cầu hợp tác ngay trên trang.
        </p>
        <div class="mt-8 flex flex-wrap gap-3">
          <a href="#creators" class="rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200">Khám phá creator</a>
          <div class="rounded-full border border-white/12 px-5 py-3 text-sm text-slate-200">Khách cũng có thể đặt lịch</div>
        </div>
      </div>

      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
        <div class="theme-card rounded-[2rem] p-5">
          <p class="text-sm uppercase tracking-[0.24em] text-fuchsia-200">Quy trình nhanh</p>
          <h2 class="mt-3 text-xl font-semibold text-white">Đặt lịch khách hoặc tự điền khi đăng nhập</h2>
          <p class="mt-3 text-sm leading-6 text-slate-300">Khách hàng đăng nhập để tự điền hồ sơ; khách chưa đăng nhập vẫn gửi yêu cầu trực tiếp được.</p>
        </div>
        <div class="theme-card rounded-[2rem] p-5">
          <p class="text-sm uppercase tracking-[0.24em] text-emerald-200">Hồ sơ tùy chỉnh</p>
          <h2 class="mt-3 text-xl font-semibold text-white">Layout theo theme và màu động</h2>
          <p class="mt-3 text-sm leading-6 text-slate-300">Mỗi trang chi tiết creator theo nhận diện và thứ tự block mà họ chọn.</p>
        </div>
      </div>
    </div>

    <section id="creators" class="mt-16">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p class="text-sm uppercase tracking-[0.28em] text-sky-300">Creators</p>
          <h2 class="mt-3 text-3xl font-semibold text-white">KOL nổi bật</h2>
        </div>
        <div class="flex w-full flex-col gap-2 sm:w-auto sm:items-end">
          <p class="text-sm text-slate-400">{{ filteredKols.length }} / {{ featuredKols.length }} hồ sơ</p>
          <input
            v-model="query"
            type="search"
            placeholder="Tìm creator..."
            class="h-11 w-full rounded-full border border-white/10 bg-white/5 px-4 text-sm text-white outline-none placeholder:text-slate-500 focus:border-sky-400/40 sm:w-72"
          />
        </div>
      </div>

      <div v-if="isLoading" class="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div v-for="index in 6" :key="index" class="h-72 animate-pulse rounded-[2rem] border border-white/10 bg-white/5"></div>
      </div>

      <div v-else-if="loadFailed" class="mt-8 rounded-[2rem] border border-rose-400/20 bg-rose-500/10 p-6 text-rose-100">
        {{ loadError || "Không tải được danh sách creator. Vui lòng thử lại sau." }}
      </div>

      <div v-else-if="!filteredKols.length" class="mt-8 rounded-[2rem] border border-white/10 bg-white/6 p-6 text-slate-200">
        {{ query.trim() ? "Không tìm thấy creator phù hợp." : "Chưa có creator công khai." }}
      </div>

      <template v-else>
        <div class="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          <KolCard v-for="kol in pagedKols" :key="kol.user_id" :kol="kol" />
        </div>

        <div
          class="mt-6 flex flex-col gap-3 rounded-[1.5rem] border border-white/10 bg-white/5 px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
        >
          <p class="text-sm text-slate-400">
            Hiển thị
            <span class="font-semibold text-white">{{ rangeStart }}–{{ rangeEnd }}</span>
            / {{ filteredKols.length }}
          </p>
          <div class="flex items-center gap-2">
            <button
              type="button"
              class="h-9 rounded-lg border border-white/10 px-3 text-sm text-slate-200 disabled:opacity-40"
              :disabled="page <= 1"
              @click="page -= 1"
            >
              Trước
            </button>
            <span class="px-2 text-sm text-slate-300">{{ page }} / {{ totalPages }}</span>
            <button
              type="button"
              class="h-9 rounded-lg border border-white/10 px-3 text-sm text-slate-200 disabled:opacity-40"
              :disabled="page >= totalPages"
              @click="page += 1"
            >
              Sau
            </button>
          </div>
        </div>
      </template>
    </section>
  </section>
</template>

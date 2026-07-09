<script setup lang="ts">
import Link from '@tiptap/extension-link'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import { onBeforeUnmount, watch } from 'vue'
import { normalizeEditorHtml, plainTextToHtml } from '@/lib/richText'

const props = withDefaults(
  defineProps<{
    modelValue: string
    placeholder?: string
    minHeight?: string
  }>(),
  {
    placeholder: 'Nhập nội dung...',
    minHeight: '12rem',
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const editor = useEditor({
  content: plainTextToHtml(props.modelValue),
  extensions: [
    StarterKit.configure({
      heading: {
        levels: [2, 3],
      },
    }),
    Underline,
    Link.configure({
      openOnClick: false,
      HTMLAttributes: {
        rel: 'noopener noreferrer',
        target: '_blank',
      },
    }),
  ],
  editorProps: {
    attributes: {
      class: 'rich-text-editor__content',
      'data-placeholder': props.placeholder,
    },
  },
  onUpdate: ({ editor: currentEditor }) => {
    emit('update:modelValue', normalizeEditorHtml(currentEditor.getHTML()))
  },
})

watch(
  () => props.modelValue,
  (value) => {
    if (!editor.value) return

    const nextHtml = plainTextToHtml(value)
    const currentHtml = normalizeEditorHtml(editor.value.getHTML())
    if (currentHtml !== normalizeEditorHtml(nextHtml)) {
      editor.value.commands.setContent(nextHtml || '<p></p>', { emitUpdate: false })
    }
  },
)

onBeforeUnmount(() => {
  editor.value?.destroy()
})

function run(action: () => void) {
  action()
  editor.value?.commands.focus()
}

function setLink() {
  if (!editor.value) return

  const previousUrl = editor.value.getAttributes('link').href as string | undefined
  const url = window.prompt('Nhập link URL', previousUrl ?? 'https://')

  if (url === null) return
  if (url === '') {
    editor.value.chain().focus().extendMarkRange('link').unsetLink().run()
    return
  }

  editor.value.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
}
</script>

<template>
  <div class="rich-text-editor" :style="{ '--rich-text-min-height': minHeight }">
    <div v-if="editor" class="rich-text-editor__toolbar">
      <button
        type="button"
        class="rich-text-editor__btn"
        :class="{ 'rich-text-editor__btn--active': editor.isActive('bold') }"
        title="In đậm"
        @click="run(() => editor?.chain().focus().toggleBold().run())"
      >
        <strong>B</strong>
      </button>
      <button
        type="button"
        class="rich-text-editor__btn"
        :class="{ 'rich-text-editor__btn--active': editor.isActive('italic') }"
        title="In nghiêng"
        @click="run(() => editor?.chain().focus().toggleItalic().run())"
      >
        <em>I</em>
      </button>
      <button
        type="button"
        class="rich-text-editor__btn"
        :class="{ 'rich-text-editor__btn--active': editor.isActive('underline') }"
        title="Gạch chân"
        @click="run(() => editor?.chain().focus().toggleUnderline().run())"
      >
        <span class="underline">U</span>
      </button>
      <span class="rich-text-editor__divider" />
      <button
        type="button"
        class="rich-text-editor__btn"
        :class="{ 'rich-text-editor__btn--active': editor.isActive('heading', { level: 2 }) }"
        title="Tiêu đề lớn"
        @click="run(() => editor?.chain().focus().toggleHeading({ level: 2 }).run())"
      >
        H2
      </button>
      <button
        type="button"
        class="rich-text-editor__btn"
        :class="{ 'rich-text-editor__btn--active': editor.isActive('heading', { level: 3 }) }"
        title="Tiêu đề nhỏ"
        @click="run(() => editor?.chain().focus().toggleHeading({ level: 3 }).run())"
      >
        H3
      </button>
      <span class="rich-text-editor__divider" />
      <button
        type="button"
        class="rich-text-editor__btn"
        :class="{ 'rich-text-editor__btn--active': editor.isActive('bulletList') }"
        title="Danh sách chấm"
        @click="run(() => editor?.chain().focus().toggleBulletList().run())"
      >
        •
      </button>
      <button
        type="button"
        class="rich-text-editor__btn"
        :class="{ 'rich-text-editor__btn--active': editor.isActive('orderedList') }"
        title="Danh sách số"
        @click="run(() => editor?.chain().focus().toggleOrderedList().run())"
      >
        1.
      </button>
      <button
        type="button"
        class="rich-text-editor__btn"
        :class="{ 'rich-text-editor__btn--active': editor.isActive('blockquote') }"
        title="Trích dẫn"
        @click="run(() => editor?.chain().focus().toggleBlockquote().run())"
      >
        “
      </button>
      <span class="rich-text-editor__divider" />
      <button
        type="button"
        class="rich-text-editor__btn"
        :class="{ 'rich-text-editor__btn--active': editor.isActive('link') }"
        title="Chèn link"
        @click="setLink"
      >
        Link
      </button>
    </div>

    <EditorContent :editor="editor" class="rich-text-editor__surface" />
  </div>
</template>

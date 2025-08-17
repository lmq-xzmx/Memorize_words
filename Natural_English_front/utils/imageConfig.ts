/**
 * 图片配置工具
 * 统一管理系统中的默认占位符图片
 */

// 图片类型枚举
export enum ImageType {
  WORD_EXAMPLE = 'word_example',
  USER_AVATAR = 'user_avatar',
  COURSE_COVER = 'course_cover',
  ARTICLE_COVER = 'article_cover'
}

// 默认占位符图片路径
export const DEFAULT_PLACEHOLDER: string = '/lost.jpg';

// 图片类型配置
export const IMAGE_TYPES = {
  WORD_EXAMPLE: 'word_example' as const,
  USER_AVATAR: 'user_avatar' as const,
  COURSE_COVER: 'course_cover' as const,
  ARTICLE_COVER: 'article_cover' as const
} as const;

// 获取默认占位符图片
export function getDefaultPlaceholder(type: ImageType | string | null = null): string {
  // 根据不同类型可以返回不同的占位符
  // 目前统一使用 lost.jpg
  return DEFAULT_PLACEHOLDER;
}

// 图片加载错误处理
export function handleImageError(event: Event, fallbackSrc: string | null = null): void {
  const img = event.target as HTMLImageElement;
  const fallback = fallbackSrc || getDefaultPlaceholder();
  
  // 避免无限循环
  if (img.src !== fallback) {
    img.src = fallback;
  }
}

// 预加载图片
export function preloadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`Failed to load image: ${src}`));
    img.src = src;
  });
}

// 检查图片是否存在
export async function checkImageExists(src: string): Promise<boolean> {
  try {
    await preloadImage(src);
    return true;
  } catch {
    return false;
  }
}

// 获取安全的图片源（如果原图片不存在则返回占位符）
export async function getSafeImageSrc(src: string | null, type: ImageType | string | null = null): Promise<string> {
  if (!src) {
    return getDefaultPlaceholder(type);
  }
  
  const exists = await checkImageExists(src);
  return exists ? src : getDefaultPlaceholder(type);
}

export default {
  DEFAULT_PLACEHOLDER,
  IMAGE_TYPES,
  getDefaultPlaceholder,
  handleImageError,
  preloadImage,
  checkImageExists,
  getSafeImageSrc
};
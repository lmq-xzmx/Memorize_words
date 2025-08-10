/**
 * 图片配置工具
 * 统一管理系统中的默认占位符图片
 */

// 默认占位符图片路径
export const DEFAULT_PLACEHOLDER = '/lost.jpg';

// 图片类型配置
export const IMAGE_TYPES = {
  WORD_EXAMPLE: 'word_example',
  USER_AVATAR: 'user_avatar',
  COURSE_COVER: 'course_cover',
  ARTICLE_COVER: 'article_cover'
};

// 获取默认占位符图片
export function getDefaultPlaceholder(type = null) {
  // 根据不同类型可以返回不同的占位符
  // 目前统一使用 lost.jpg
  return DEFAULT_PLACEHOLDER;
}

// 图片加载错误处理
export function handleImageError(event, fallbackSrc = null) {
  const img = event.target;
  const fallback = fallbackSrc || getDefaultPlaceholder();
  
  // 避免无限循环
  if (img.src !== fallback) {
    img.src = fallback;
  }
}

// 预加载图片
export function preloadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`Failed to load image: ${src}`));
    img.src = src;
  });
}

// 检查图片是否存在
export async function checkImageExists(src) {
  try {
    await preloadImage(src);
    return true;
  } catch {
    return false;
  }
}

// 获取安全的图片源（如果原图片不存在则返回占位符）
export async function getSafeImageSrc(src, type = null) {
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
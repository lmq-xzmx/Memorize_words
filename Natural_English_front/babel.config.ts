import type { ConfigAPI, TransformOptions } from '@babel/core'

export default function(api: ConfigAPI): TransformOptions {
  api.cache.forever()
  
  return {
    presets: [
      [
        '@babel/preset-env',
        {
          targets: {
            node: 'current'
          }
        }
      ],
      '@babel/preset-typescript'
    ],
    env: {
      test: {
        presets: [
          [
            '@babel/preset-env',
            {
              targets: {
                node: 'current'
              }
            }
          ],
          '@babel/preset-typescript'
        ]
      }
    }
  }
}
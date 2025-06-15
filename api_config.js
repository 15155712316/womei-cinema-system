/**
 * API配置管理 - 影院连锁系统适配
 * 支持华联和沃美两个影院连锁系统的API配置
 */

// 系统配置枚举
const CINEMA_SYSTEMS = {
  HUANLIAN: 'huanlian',
  WOMEI: 'womei'
};

// 影院连锁系统配置
const CINEMA_CONFIGS = {
  [CINEMA_SYSTEMS.HUANLIAN]: {
    systemName: '华联连锁影院',
    apiConfig: {
      baseUrl: 'https://ct.vistachina.cn',
      tenantShort: 'HLYC2020',
      channelId: '40000',
      clientVersion: '4.0',
      wxAppId: 'wx49c1f7da49fea68c',
      // 注意：实际开发中token应该通过登录接口动态获取
      defaultToken: 'ede3e426eb22b865f071a40e6d676ecf'
    },
    endpoints: {
      cities: '/ticket/{tenantShort}/citys/',
      cinemas: '/ticket/{tenantShort}/cinemas/',
      movies: '/ticket/{tenantShort}/movies/',
      sessions: '/ticket/{tenantShort}/sessions/',
      order: '/ticket/{tenantShort}/order/'
    }
  },
  
  [CINEMA_SYSTEMS.WOMEI]: {
    systemName: '沃美连锁影院',
    apiConfig: {
      baseUrl: 'https://ct.womovie.cn',
      tenantShort: 'wmyc',
      channelId: '40000',
      clientVersion: '4.0',
      wxAppId: 'wx4bb9342b9d97d53c',
      // 注意：实际开发中token应该通过登录接口动态获取
      defaultToken: 'b0779d60d098e77e36cbae0545e8ddc3'
    },
    endpoints: {
      cities: '/ticket/{tenantShort}/citys/',
      cinemas: '/ticket/{tenantShort}/cinemas/',
      movies: '/ticket/{tenantShort}/movies/',
      sessions: '/ticket/{tenantShort}/sessions/',
      order: '/ticket/{tenantShort}/order/'
    }
  }
};

// 通用请求头配置
const COMMON_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
  'content-type': 'multipart/form-data',
  'xweb_xhr': '1',
  'x-requested-with': 'wxapp',
  'sec-fetch-site': 'cross-site',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'accept-language': 'zh-CN,zh;q=0.9',
  'priority': 'u=1, i'
};

/**
 * 获取指定影院系统的配置
 * @param {string} systemType - 影院系统类型
 * @returns {Object} 系统配置对象
 */
function getCinemaConfig(systemType) {
  const config = CINEMA_CONFIGS[systemType];
  if (!config) {
    throw new Error(`不支持的影院系统类型: ${systemType}`);
  }
  return config;
}

/**
 * 构建API完整URL
 * @param {string} systemType - 影院系统类型
 * @param {string} endpoint - 接口端点
 * @returns {string} 完整的API URL
 */
function buildApiUrl(systemType, endpoint) {
  const config = getCinemaConfig(systemType);
  const { baseUrl, tenantShort } = config.apiConfig;
  const endpointPath = config.endpoints[endpoint];
  
  if (!endpointPath) {
    throw new Error(`不支持的接口端点: ${endpoint}`);
  }
  
  // 替换路径中的占位符
  const path = endpointPath.replace('{tenantShort}', tenantShort);
  return `${baseUrl}${path}`;
}

/**
 * 构建请求头
 * @param {string} systemType - 影院系统类型
 * @param {string} token - 认证令牌（可选，如果不提供则使用默认token）
 * @returns {Object} 完整的请求头对象
 */
function buildRequestHeaders(systemType, token = null) {
  const config = getCinemaConfig(systemType);
  const { channelId, tenantShort, clientVersion, wxAppId, defaultToken } = config.apiConfig;
  
  // 使用提供的token或默认token
  const authToken = token || defaultToken;
  
  return {
    ...COMMON_HEADERS,
    'x-channel-id': channelId,
    'tenant-short': tenantShort,
    'client-version': clientVersion,
    'token': authToken,
    'referer': `https://servicewechat.com/${wxAppId}/33/page-frame.html`
  };
}

// 导出配置和工具函数
export {
  CINEMA_SYSTEMS,
  CINEMA_CONFIGS,
  getCinemaConfig,
  buildApiUrl,
  buildRequestHeaders
};

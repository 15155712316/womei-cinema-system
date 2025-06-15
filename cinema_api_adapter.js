/**
 * 影院API适配器
 * 统一华联和沃美两个影院系统的API调用接口
 */

import { 
  CINEMA_SYSTEMS, 
  buildApiUrl, 
  buildRequestHeaders 
} from './api_config.js';

/**
 * 影院API适配器类
 */
class CinemaAPIAdapter {
  constructor(systemType, token = null) {
    this.systemType = systemType;
    this.token = token;
    
    // 验证系统类型
    if (!Object.values(CINEMA_SYSTEMS).includes(systemType)) {
      throw new Error(`不支持的影院系统类型: ${systemType}`);
    }
  }

  /**
   * 设置认证令牌
   * @param {string} token - 认证令牌
   */
  setToken(token) {
    this.token = token;
  }

  /**
   * 执行HTTP请求
   * @param {string} endpoint - 接口端点
   * @param {Object} options - 请求选项
   * @returns {Promise} 请求结果
   */
  async request(endpoint, options = {}) {
    const url = buildApiUrl(this.systemType, endpoint);
    const headers = buildRequestHeaders(this.systemType, this.token);
    
    const requestOptions = {
      method: 'GET',
      headers,
      ...options
    };

    try {
      console.log(`[${this.systemType}] 请求API: ${url}`);
      
      const response = await fetch(url, requestOptions);
      
      if (!response.ok) {
        throw new Error(`HTTP错误: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log(`[${this.systemType}] API响应成功`);
      
      return data;
    } catch (error) {
      console.error(`[${this.systemType}] API请求失败:`, error);
      throw error;
    }
  }

  /**
   * 获取城市列表
   * @returns {Promise<Array>} 城市列表
   */
  async getCities() {
    return await this.request('cities');
  }

  /**
   * 获取影院列表
   * @param {string} cityId - 城市ID（可选）
   * @returns {Promise<Array>} 影院列表
   */
  async getCinemas(cityId = null) {
    const options = {};
    if (cityId) {
      // 如果需要城市参数，可以在这里添加
      options.body = new FormData();
      options.body.append('cityId', cityId);
      options.method = 'POST';
    }
    return await this.request('cinemas', options);
  }

  /**
   * 获取电影列表
   * @param {string} cinemaId - 影院ID（可选）
   * @returns {Promise<Array>} 电影列表
   */
  async getMovies(cinemaId = null) {
    const options = {};
    if (cinemaId) {
      options.body = new FormData();
      options.body.append('cinemaId', cinemaId);
      options.method = 'POST';
    }
    return await this.request('movies', options);
  }

  /**
   * 获取场次列表
   * @param {Object} params - 查询参数
   * @returns {Promise<Array>} 场次列表
   */
  async getSessions(params = {}) {
    const options = {
      method: 'POST',
      body: new FormData()
    };
    
    // 添加查询参数
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined) {
        options.body.append(key, params[key]);
      }
    });
    
    return await this.request('sessions', options);
  }

  /**
   * 创建订单
   * @param {Object} orderData - 订单数据
   * @returns {Promise<Object>} 订单结果
   */
  async createOrder(orderData) {
    const options = {
      method: 'POST',
      body: new FormData()
    };
    
    // 添加订单数据
    Object.keys(orderData).forEach(key => {
      if (orderData[key] !== null && orderData[key] !== undefined) {
        options.body.append(key, orderData[key]);
      }
    });
    
    return await this.request('order', options);
  }
}

/**
 * 创建影院API适配器实例
 * @param {string} systemType - 影院系统类型
 * @param {string} token - 认证令牌（可选）
 * @returns {CinemaAPIAdapter} API适配器实例
 */
function createCinemaAPI(systemType, token = null) {
  return new CinemaAPIAdapter(systemType, token);
}

/**
 * 华联影院API实例
 */
const HuanlianAPI = {
  create: (token) => createCinemaAPI(CINEMA_SYSTEMS.HUANLIAN, token)
};

/**
 * 沃美影院API实例
 */
const WomeiAPI = {
  create: (token) => createCinemaAPI(CINEMA_SYSTEMS.WOMEI, token)
};

// 导出API适配器
export {
  CinemaAPIAdapter,
  createCinemaAPI,
  HuanlianAPI,
  WomeiAPI
};

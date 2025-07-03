/**
 * API适配器使用示例
 * 演示如何使用统一的API适配器调用不同影院系统的接口
 */

import { 
  CINEMA_SYSTEMS, 
  createCinemaAPI, 
  HuanlianAPI, 
  WomeiAPI 
} from './cinema_api_adapter.js';

/**
 * 示例1: 基础API调用
 */
async function basicAPIExample() {
  console.log('=== 基础API调用示例 ===');
  
  try {
    // 创建华联影院API实例
    const huanlianAPI = createCinemaAPI(CINEMA_SYSTEMS.HUANLIAN);
    
    // 创建沃美影院API实例  
    const womeiAPI = createCinemaAPI(CINEMA_SYSTEMS.WOMEI);
    
    // 获取华联影院城市列表
    console.log('获取华联影院城市列表...');
    const huanlianCities = await huanlianAPI.getCities();
    console.log('华联城市数量:', huanlianCities.length);
    
    // 获取沃美影院城市列表
    console.log('获取沃美影院城市列表...');
    const womeiCities = await womeiAPI.getCities();
    console.log('沃美城市数量:', womeiCities.length);
    
  } catch (error) {
    console.error('API调用失败:', error);
  }
}

/**
 * 示例2: 使用工厂方法
 */
async function factoryMethodExample() {
  console.log('=== 工厂方法示例 ===');
  
  try {
    // 使用华联API工厂方法
    const huanlianAPI = HuanlianAPI.create('your-huanlian-token');
    
    // 使用沃美API工厂方法
    const womeiAPI = WomeiAPI.create('your-womei-token');
    
    // 并行获取两个系统的城市列表
    const [huanlianCities, womeiCities] = await Promise.all([
      huanlianAPI.getCities(),
      womeiAPI.getCities()
    ]);
    
    console.log('华联城市:', huanlianCities.slice(0, 3)); // 显示前3个城市
    console.log('沃美城市:', womeiCities.slice(0, 3)); // 显示前3个城市
    
  } catch (error) {
    console.error('并行API调用失败:', error);
  }
}

/**
 * 示例3: 完整的业务流程
 */
async function completeBusinessFlowExample() {
  console.log('=== 完整业务流程示例 ===');
  
  try {
    // 根据配置选择影院系统
    const systemType = process.env.CINEMA_SYSTEM || CINEMA_SYSTEMS.WOMEI;
    const api = createCinemaAPI(systemType);
    
    console.log(`使用影院系统: ${systemType}`);
    
    // 1. 获取城市列表
    console.log('1. 获取城市列表...');
    const cities = await api.getCities();
    console.log(`找到 ${cities.length} 个城市`);
    
    if (cities.length > 0) {
      const firstCity = cities[0];
      console.log(`选择城市: ${firstCity.name || firstCity.cityName}`);
      
      // 2. 获取该城市的影院列表
      console.log('2. 获取影院列表...');
      const cinemas = await api.getCinemas(firstCity.id || firstCity.cityId);
      console.log(`找到 ${cinemas.length} 个影院`);
      
      if (cinemas.length > 0) {
        const firstCinema = cinemas[0];
        console.log(`选择影院: ${firstCinema.name || firstCinema.cinemaName}`);
        
        // 3. 获取该影院的电影列表
        console.log('3. 获取电影列表...');
        const movies = await api.getMovies(firstCinema.id || firstCinema.cinemaId);
        console.log(`找到 ${movies.length} 部电影`);
        
        if (movies.length > 0) {
          const firstMovie = movies[0];
          console.log(`选择电影: ${firstMovie.name || firstMovie.movieName}`);
          
          // 4. 获取场次列表
          console.log('4. 获取场次列表...');
          const sessions = await api.getSessions({
            cinemaId: firstCinema.id || firstCinema.cinemaId,
            movieId: firstMovie.id || firstMovie.movieId,
            date: new Date().toISOString().split('T')[0] // 今天的日期
          });
          console.log(`找到 ${sessions.length} 个场次`);
        }
      }
    }
    
  } catch (error) {
    console.error('业务流程执行失败:', error);
  }
}

/**
 * 示例4: 错误处理和重试机制
 */
async function errorHandlingExample() {
  console.log('=== 错误处理示例 ===');
  
  const api = createCinemaAPI(CINEMA_SYSTEMS.WOMEI);
  
  // 带重试的API调用
  async function apiCallWithRetry(apiCall, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await apiCall();
      } catch (error) {
        console.log(`第 ${i + 1} 次尝试失败:`, error.message);
        
        if (i === maxRetries - 1) {
          throw error; // 最后一次尝试失败，抛出错误
        }
        
        // 等待一段时间后重试
        await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
      }
    }
  }
  
  try {
    const cities = await apiCallWithRetry(() => api.getCities());
    console.log('重试成功，获取到城市列表:', cities.length);
  } catch (error) {
    console.error('重试失败:', error);
  }
}

/**
 * 示例5: 系统切换演示
 */
async function systemSwitchExample() {
  console.log('=== 系统切换示例 ===');
  
  const systems = [CINEMA_SYSTEMS.HUANLIAN, CINEMA_SYSTEMS.WOMEI];
  
  for (const systemType of systems) {
    try {
      console.log(`\n切换到 ${systemType} 系统:`);
      const api = createCinemaAPI(systemType);
      
      const cities = await api.getCities();
      console.log(`${systemType} 系统城市数量:`, cities.length);
      
      // 显示前几个城市名称
      const cityNames = cities.slice(0, 3).map(city => 
        city.name || city.cityName || '未知城市'
      );
      console.log(`前3个城市: ${cityNames.join(', ')}`);
      
    } catch (error) {
      console.error(`${systemType} 系统调用失败:`, error.message);
    }
  }
}

// 运行示例（在实际项目中根据需要调用）
async function runExamples() {
  await basicAPIExample();
  await factoryMethodExample();
  await completeBusinessFlowExample();
  await errorHandlingExample();
  await systemSwitchExample();
}

// 导出示例函数
export {
  basicAPIExample,
  factoryMethodExample,
  completeBusinessFlowExample,
  errorHandlingExample,
  systemSwitchExample,
  runExamples
};

// 如果直接运行此文件，执行所有示例
if (import.meta.url === `file://${process.argv[1]}`) {
  runExamples().catch(console.error);
}

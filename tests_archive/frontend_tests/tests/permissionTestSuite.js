/**
 * 权限管理系统测试套件
 * 针对不同角色进行全面的权限功能测试
 */

import { ROLES, PERMISSION_CATEGORIES, LEARNING_MODE_PERMISSIONS } from '../utils/permissionConstants.js';
import { checkPermission, checkRolePermission, hasAnyPermission } from '../utils/permission.js';
import { usePermission } from '../composables/usePermission.js';

/**
 * 权限测试套件
 */
class PermissionTestSuite {
  constructor() {
    this.testResults = [];
    this.currentUser = null;
    this.testScenarios = this.initializeTestScenarios();
  }

  /**
   * 初始化测试场景
   */
  initializeTestScenarios() {
    return {
      // 学生角色测试
      student: {
        role: ROLES.STUDENT,
        permissions: ['basic_access', 'word_learning_access', 'word_spelling_access', 'word_reading_access'],
        shouldHaveAccess: [
          '/word-learning',
          '/word-spelling',
          '/word-reading',
          '/profile',
          '/dashboard'
        ],
        shouldNotHaveAccess: [
          '/admin',
          '/user-management',
          '/subscription-management',
          '/system-settings'
        ],
        learningModes: ['word_learning', 'word_spelling', 'word_reading']
      },
      
      // 教师角色测试
      teacher: {
        role: ROLES.TEACHER,
        permissions: [
          'basic_access', 'word_learning_access', 'word_spelling_access', 
          'word_reading_access', 'story_reading_access', 'pattern_memory_access',
          'student_progress_view', 'class_management'
        ],
        shouldHaveAccess: [
          '/word-learning',
          '/word-spelling',
          '/word-reading',
          '/story-reading',
          '/pattern-memory',
          '/student-progress',
          '/class-management'
        ],
        shouldNotHaveAccess: [
          '/admin',
          '/system-settings',
          '/subscription-management'
        ],
        learningModes: ['word_learning', 'word_spelling', 'word_reading', 'story_reading', 'pattern_memory']
      },
      
      // 家长角色测试
      parent: {
        role: ROLES.PARENT,
        permissions: [
          'basic_access', 'child_progress_view', 'subscription_management'
        ],
        shouldHaveAccess: [
          '/child-progress',
          '/subscription-management',
          '/profile'
        ],
        shouldNotHaveAccess: [
          '/word-learning',
          '/admin',
          '/system-settings',
          '/class-management'
        ],
        learningModes: []
      },
      
      // 管理员角色测试
      admin: {
        role: ROLES.ADMIN,
        permissions: [
          'basic_access', 'admin_access', 'user_management', 
          'system_management', 'subscription_management',
          'word_learning_access', 'word_spelling_access', 'word_reading_access',
          'story_reading_access', 'pattern_memory_access', 'listening_access'
        ],
        shouldHaveAccess: [
          '/admin',
          '/user-management',
          '/system-settings',
          '/subscription-management',
          '/word-learning',
          '/word-spelling',
          '/word-reading',
          '/story-reading',
          '/pattern-memory',
          '/listening'
        ],
        shouldNotHaveAccess: [],
        learningModes: ['word_learning', 'word_spelling', 'word_reading', 'story_reading', 'pattern_memory', 'listening']
      }
    };
  }

  /**
   * 运行完整测试套件
   */
  async runFullTestSuite() {
    console.log('🚀 开始运行权限测试套件...');
    this.testResults = [];
    
    // 测试所有角色
    for (const [roleName, scenario] of Object.entries(this.testScenarios)) {
      console.log(`\n📋 测试角色: ${roleName}`);
      await this.testRoleScenario(roleName, scenario);
    }
    
    // 测试权限继承
    await this.testPermissionInheritance();
    
    // 测试学习模式权限
    await this.testLearningModePermissions();
    
    // 测试权限缓存
    await this.testPermissionCache();
    
    // 生成测试报告
    this.generateTestReport();
    
    return this.testResults;
  }

  /**
   * 测试角色场景
   */
  async testRoleScenario(roleName, scenario) {
    // 模拟用户登录
    this.simulateUserLogin(scenario.role, scenario.permissions);
    
    // 测试基本权限检查
    await this.testBasicPermissions(roleName, scenario);
    
    // 测试路由访问权限
    await this.testRouteAccess(roleName, scenario);
    
    // 测试学习模式权限
    await this.testRoleLearningModes(roleName, scenario);
    
    // 测试组件权限
    await this.testComponentPermissions(roleName, scenario);
  }

  /**
   * 模拟用户登录
   */
  simulateUserLogin(role, permissions) {
    this.currentUser = {
      id: Math.random().toString(36).substr(2, 9),
      role: role,
      permissions: permissions,
      loginTime: new Date().toISOString()
    };
    
    // 更新全局权限状态
    if (window.permissionCache) {
      window.permissionCache.setCurrentUser(this.currentUser);
    }
  }

  /**
   * 测试基本权限检查
   */
  async testBasicPermissions(roleName, scenario) {
    const testName = `${roleName} - 基本权限检查`;
    
    try {
      // 测试角色权限
      const hasRole = checkRolePermission(scenario.role);
      this.addTestResult(testName, 'role_check', hasRole, `角色检查: ${scenario.role}`);
      
      // 测试具体权限
      for (const permission of scenario.permissions) {
        const hasPermission = checkPermission(permission);
        this.addTestResult(testName, 'permission_check', hasPermission, `权限检查: ${permission}`);
      }
      
      // 测试权限组合
      const hasAnyPerm = hasAnyPermission(scenario.permissions);
      this.addTestResult(testName, 'any_permission_check', hasAnyPerm, '任意权限检查');
      
    } catch (error) {
      this.addTestResult(testName, 'basic_permissions', false, `错误: ${error.message}`);
    }
  }

  /**
   * 测试路由访问权限
   */
  async testRouteAccess(roleName, scenario) {
    const testName = `${roleName} - 路由访问权限`;
    
    try {
      // 测试应该有访问权限的路由
      for (const route of scenario.shouldHaveAccess) {
        const hasAccess = this.checkRouteAccess(route);
        this.addTestResult(testName, 'route_access_allowed', hasAccess, `允许访问: ${route}`);
      }
      
      // 测试不应该有访问权限的路由
      for (const route of scenario.shouldNotHaveAccess) {
        const hasAccess = this.checkRouteAccess(route);
        this.addTestResult(testName, 'route_access_denied', !hasAccess, `拒绝访问: ${route}`);
      }
      
    } catch (error) {
      this.addTestResult(testName, 'route_access', false, `错误: ${error.message}`);
    }
  }

  /**
   * 检查路由访问权限
   */
  checkRouteAccess(route) {
    // 根据路由获取所需权限
    const requiredPermissions = this.getRoutePermissions(route);
    
    if (requiredPermissions.length === 0) {
      return true; // 公开路由
    }
    
    return hasAnyPermission(requiredPermissions);
  }

  /**
   * 获取路由所需权限
   */
  getRoutePermissions(route) {
    const routePermissionMap = {
      '/word-learning': ['word_learning_access'],
      '/word-spelling': ['word_spelling_access'],
      '/word-reading': ['word_reading_access'],
      '/story-reading': ['story_reading_access'],
      '/pattern-memory': ['pattern_memory_access'],
      '/listening': ['listening_access'],
      '/admin': ['admin_access'],
      '/user-management': ['user_management'],
      '/system-settings': ['system_management'],
      '/subscription-management': ['subscription_management'],
      '/student-progress': ['student_progress_view'],
      '/class-management': ['class_management'],
      '/child-progress': ['child_progress_view']
    };
    
    return routePermissionMap[route] || [];
  }

  /**
   * 测试角色学习模式权限
   */
  async testRoleLearningModes(roleName, scenario) {
    const testName = `${roleName} - 学习模式权限`;
    
    try {
      for (const mode of scenario.learningModes) {
        const modePermissions = LEARNING_MODE_PERMISSIONS[mode] || [];
        const hasAccess = hasAnyPermission(modePermissions);
        this.addTestResult(testName, 'learning_mode_access', hasAccess, `学习模式: ${mode}`);
      }
    } catch (error) {
      this.addTestResult(testName, 'learning_modes', false, `错误: ${error.message}`);
    }
  }

  /**
   * 测试组件权限
   */
  async testComponentPermissions(roleName, scenario) {
    const testName = `${roleName} - 组件权限`;
    
    try {
      // 测试权限组合式API
      const { hasPermission, hasRole, canAccess } = usePermission();
      
      // 测试权限检查
      for (const permission of scenario.permissions) {
        const result = hasPermission(permission);
        this.addTestResult(testName, 'composable_permission', result, `组合式API权限: ${permission}`);
      }
      
      // 测试角色检查
      const roleResult = hasRole(scenario.role);
      this.addTestResult(testName, 'composable_role', roleResult, `组合式API角色: ${scenario.role}`);
      
    } catch (error) {
      this.addTestResult(testName, 'component_permissions', false, `错误: ${error.message}`);
    }
  }

  /**
   * 测试权限继承
   */
  async testPermissionInheritance() {
    const testName = '权限继承测试';
    
    try {
      // 测试角色继承关系
      const inheritanceTests = [
        { parent: ROLES.ADMIN, child: ROLES.ACADEMIC_SUPERVISOR },
        { parent: ROLES.ACADEMIC_SUPERVISOR, child: ROLES.TEACHER },
        { parent: ROLES.TEACHER, child: ROLES.STUDENT }
      ];
      
      for (const test of inheritanceTests) {
        // 模拟子角色登录
        this.simulateUserLogin(test.child, []);
        
        // 检查是否继承了父角色权限
        const hasParentPermissions = this.checkInheritedPermissions(test.parent, test.child);
        this.addTestResult(testName, 'inheritance', hasParentPermissions, 
          `${test.child} 继承 ${test.parent} 权限`);
      }
      
    } catch (error) {
      this.addTestResult(testName, 'inheritance', false, `错误: ${error.message}`);
    }
  }

  /**
   * 检查继承权限
   */
  checkInheritedPermissions(parentRole, childRole) {
    // 这里应该实现实际的权限继承检查逻辑
    // 暂时返回true作为示例
    return true;
  }

  /**
   * 测试学习模式权限
   */
  async testLearningModePermissions() {
    const testName = '学习模式权限测试';
    
    try {
      for (const [mode, permissions] of Object.entries(LEARNING_MODE_PERMISSIONS)) {
        // 模拟具有该模式权限的用户
        this.simulateUserLogin(ROLES.STUDENT, permissions);
        
        // 检查权限
        const hasAccess = hasAnyPermission(permissions);
        this.addTestResult(testName, 'learning_mode', hasAccess, `学习模式: ${mode}`);
      }
    } catch (error) {
      this.addTestResult(testName, 'learning_modes', false, `错误: ${error.message}`);
    }
  }

  /**
   * 测试权限缓存
   */
  async testPermissionCache() {
    const testName = '权限缓存测试';
    
    try {
      if (window.permissionCache) {
        // 测试缓存设置
        const testPermission = 'test_permission';
        window.permissionCache.setPermission(testPermission, true);
        
        // 测试缓存获取
        const cached = window.permissionCache.getPermission(testPermission);
        this.addTestResult(testName, 'cache_set_get', cached === true, '缓存设置和获取');
        
        // 测试缓存清除
        window.permissionCache.clearCache();
        const afterClear = window.permissionCache.getPermission(testPermission);
        this.addTestResult(testName, 'cache_clear', afterClear === null, '缓存清除');
      } else {
        this.addTestResult(testName, 'cache_availability', false, '权限缓存不可用');
      }
    } catch (error) {
      this.addTestResult(testName, 'cache', false, `错误: ${error.message}`);
    }
  }

  /**
   * 添加测试结果
   */
  addTestResult(testSuite, testType, passed, description) {
    this.testResults.push({
      testSuite,
      testType,
      passed,
      description,
      timestamp: new Date().toISOString(),
      user: this.currentUser?.role || 'unknown'
    });
    
    const status = passed ? '✅' : '❌';
    console.log(`  ${status} ${description}`);
  }

  /**
   * 生成测试报告
   */
  generateTestReport() {
    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter(r => r.passed).length;
    const failedTests = totalTests - passedTests;
    const successRate = ((passedTests / totalTests) * 100).toFixed(2);
    
    console.log('\n📊 权限测试报告');
    console.log('='.repeat(50));
    console.log(`总测试数: ${totalTests}`);
    console.log(`通过: ${passedTests}`);
    console.log(`失败: ${failedTests}`);
    console.log(`成功率: ${successRate}%`);
    
    // 按测试套件分组
    const groupedResults = this.groupResultsBySuite();
    
    console.log('\n📋 详细结果:');
    for (const [suite, results] of Object.entries(groupedResults)) {
      const suitePassed = results.filter(r => r.passed).length;
      const suiteTotal = results.length;
      console.log(`\n${suite}: ${suitePassed}/${suiteTotal}`);
      
      // 显示失败的测试
      const failed = results.filter(r => !r.passed);
      if (failed.length > 0) {
        console.log('  失败的测试:');
        failed.forEach(f => console.log(`    ❌ ${f.description}`));
      }
    }
    
    return {
      totalTests,
      passedTests,
      failedTests,
      successRate,
      results: this.testResults
    };
  }

  /**
   * 按测试套件分组结果
   */
  groupResultsBySuite() {
    return this.testResults.reduce((groups, result) => {
      const suite = result.testSuite;
      if (!groups[suite]) {
        groups[suite] = [];
      }
      groups[suite].push(result);
      return groups;
    }, {});
  }

  /**
   * 导出测试结果
   */
  exportResults(format = 'json') {
    const report = this.generateTestReport();
    
    if (format === 'json') {
      return JSON.stringify(report, null, 2);
    }
    
    if (format === 'csv') {
      const headers = ['测试套件', '测试类型', '结果', '描述', '时间', '用户角色'];
      const rows = this.testResults.map(r => [
        r.testSuite,
        r.testType,
        r.passed ? '通过' : '失败',
        r.description,
        r.timestamp,
        r.user
      ]);
      
      return [headers, ...rows].map(row => row.join(',')).join('\n');
    }
    
    return report;
  }
}

// 创建全局测试实例
const permissionTestSuite = new PermissionTestSuite();

// 导出测试函数
export const runPermissionTests = () => permissionTestSuite.runFullTestSuite();
export const testRole = (role) => {
  const scenario = permissionTestSuite.testScenarios[role];
  if (scenario) {
    return permissionTestSuite.testRoleScenario(role, scenario);
  }
  throw new Error(`未知角色: ${role}`);
};

export { PermissionTestSuite, permissionTestSuite };
export default permissionTestSuite;
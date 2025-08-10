from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.conf import settings
import json
import csv
import io
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProgressReportView:
    """进度报告视图类"""
    
    @staticmethod
    @login_required
    def report_dashboard(request):
        """报告仪表板页面"""
        context = {
            'report_title': '九宫格进程',
            'report_subtitle': '学习进度分析',
            'progress_data': ProgressReportView._get_default_progress_data()
        }
        return render(request, 'reports/progress_report.html', context)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @login_required
    def upload_data(request):
        """处理数据上传"""
        try:
            if 'files' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'error': '没有上传文件'
                })
            
            uploaded_files = request.FILES.getlist('files')
            processed_data = []
            
            for file in uploaded_files:
                try:
                    data = ProgressReportView._process_uploaded_file(file)
                    processed_data.extend(data)
                except Exception as e:
                    logger.error(f"处理文件 {file.name} 时出错: {str(e)}")
                    return JsonResponse({
                        'success': False,
                        'error': f'处理文件 {file.name} 时出错: {str(e)}'
                    })
            
            # 保存处理后的数据到会话中
            request.session['uploaded_data'] = processed_data
            
            return JsonResponse({
                'success': True,
                'data_count': len(processed_data),
                'message': f'成功处理 {len(uploaded_files)} 个文件，共 {len(processed_data)} 条记录'
            })
            
        except Exception as e:
            logger.error(f"上传数据时出错: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'上传失败: {str(e)}'
            })
    
    @staticmethod
    @require_http_methods(["POST"])
    @login_required
    def generate_report(request):
        """生成报告数据"""
        try:
            # 从会话中获取上传的数据
            uploaded_data = request.session.get('uploaded_data', [])
            
            if not uploaded_data:
                # 如果没有上传数据，使用默认示例数据
                report_data = ProgressReportView._get_default_progress_data()
            else:
                # 处理上传的数据
                report_data = ProgressReportView._process_report_data(uploaded_data)
            
            # 计算统计信息
            stats = ProgressReportView._calculate_stats(report_data)
            
            return JsonResponse({
                'success': True,
                'report_data': report_data,
                'stats': stats,
                'message': '报告生成成功'
            })
            
        except Exception as e:
            logger.error(f"生成报告时出错: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'生成报告失败: {str(e)}'
            })
    
    @staticmethod
    @require_http_methods(["POST"])
    @login_required
    def export_report(request):
        """导出报告"""
        try:
            data = json.loads(request.body)
            export_format = data.get('format', 'pdf')
            report_data = data.get('report_data', [])
            
            if export_format == 'pdf':
                # PDF导出逻辑
                file_url = ProgressReportView._export_to_pdf(report_data)
            elif export_format == 'excel':
                # Excel导出逻辑
                file_url = ProgressReportView._export_to_excel(report_data)
            elif export_format == 'image':
                # 图片导出逻辑
                file_url = ProgressReportView._export_to_image(report_data)
            else:
                return JsonResponse({
                    'success': False,
                    'error': '不支持的导出格式'
                })
            
            return JsonResponse({
                'success': True,
                'file_url': file_url,
                'message': f'{export_format.upper()} 导出成功'
            })
            
        except Exception as e:
            logger.error(f"导出报告时出错: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'导出失败: {str(e)}'
            })
    
    @staticmethod
    def _process_uploaded_file(file):
        """处理上传的文件"""
        file_extension = file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            return ProgressReportView._process_csv_file(file)
        elif file_extension in ['xlsx', 'xls']:
            return ProgressReportView._process_excel_file(file)
        elif file_extension == 'json':
            return ProgressReportView._process_json_file(file)
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
    
    @staticmethod
    def _process_csv_file(file):
        """处理CSV文件"""
        try:
            content = file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))
            return list(csv_reader)
        except UnicodeDecodeError:
            # 尝试使用GBK编码
            file.seek(0)
            content = file.read().decode('gbk')
            csv_reader = csv.DictReader(io.StringIO(content))
            return list(csv_reader)
    
    @staticmethod
    def _process_excel_file(file):
        """处理Excel文件"""
        try:
            df = pd.read_excel(file)
            return df.to_dict('records')
        except Exception as e:
            raise ValueError(f"Excel文件处理失败: {str(e)}")
    
    @staticmethod
    def _process_json_file(file):
        """处理JSON文件"""
        try:
            content = file.read().decode('utf-8')
            data = json.loads(content)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                raise ValueError("JSON文件格式不正确")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON文件解析失败: {str(e)}")
    
    @staticmethod
    def _process_report_data(uploaded_data):
        """处理报告数据"""
        categories = {
            '掌握': {'count': 0, 'color': '#4CAF50'},
            '遗忘': {'count': 0, 'color': '#f44336'},
            '学习中': {'count': 0, 'color': '#FFC107'},
            '测试': {'count': 0, 'color': '#8BC34A'},
            '口音文本': {'count': 0, 'color': '#4CAF50'},
            '口音文件': {'count': 0, 'color': '#4CAF50'},
            '区域化任务': {'count': 0, 'color': '#4CAF50'},
            '解决方案': {'count': 0, 'color': '#4CAF50'}
        }
        
        # 统计各类别数据
        for item in uploaded_data:
            category = item.get('category') or item.get('label') or item.get('type')
            value = item.get('value') or item.get('count') or 1
            
            try:
                value = int(value)
            except (ValueError, TypeError):
                value = 1
            
            if category in categories:
                categories[category]['count'] += value
        
        # 转换为前端需要的格式
        report_data = []
        for label, data in categories.items():
            report_data.append({
                'label': label,
                'value': data['count'],
                'color': data['color'],
                'category': label
            })
        
        return report_data
    
    @staticmethod
    def _get_default_progress_data():
        """获取默认的进度数据"""
        return [
            {'label': '掌握', 'value': 49, 'color': '#4CAF50', 'category': '掌握'},
            {'label': '遗忘', 'value': 0, 'color': '#f44336', 'category': '遗忘'},
            {'label': '学习中', 'value': 15, 'color': '#FFC107', 'category': '学习中'},
            {'label': '测试', 'value': 0, 'color': '#8BC34A', 'category': '测试'},
            {'label': '口音文本', 'value': 0, 'color': '#4CAF50', 'category': '口音文本'},
            {'label': '口音文件', 'value': 0, 'color': '#4CAF50', 'category': '口音文件'},
            {'label': '区域化任务', 'value': 0, 'color': '#4CAF50', 'category': '区域化任务'},
            {'label': '解决方案', 'value': 0, 'color': '#4CAF50', 'category': '解决方案'}
        ]
    
    @staticmethod
    def _calculate_stats(report_data):
        """计算统计信息"""
        total_records = sum(item['value'] for item in report_data)
        completed_items = sum(item['value'] for item in report_data 
                            if item['category'] in ['掌握', '测试'])
        pending_items = sum(item['value'] for item in report_data 
                          if item['category'] in ['学习中', '口音文本'])
        completion_rate = round((completed_items / total_records * 100) if total_records > 0 else 0, 1)
        
        return {
            'total_records': total_records,
            'completed_items': completed_items,
            'pending_items': pending_items,
            'completion_rate': completion_rate
        }
    
    @staticmethod
    def _export_to_pdf(report_data):
        """导出为PDF"""
        # 这里可以使用reportlab或weasyprint等库生成PDF
        # 简化实现，返回模拟的文件URL
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'progress_report_{timestamp}.pdf'
        return f'/media/reports/{filename}'
    
    @staticmethod
    def _export_to_excel(report_data):
        """导出为Excel"""
        # 使用pandas导出Excel
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'progress_report_{timestamp}.xlsx'
        
        try:
            df = pd.DataFrame(report_data)
            file_path = f'media/reports/{filename}'
            df.to_excel(file_path, index=False)
            return f'/{file_path}'
        except Exception as e:
            logger.error(f"Excel导出失败: {str(e)}")
            return None
    
    @staticmethod
    def _export_to_image(report_data):
        """导出为图片"""
        # 这里可以使用matplotlib或PIL等库生成图片
        # 简化实现，返回模拟的文件URL
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'progress_report_{timestamp}.png'
        return f'/media/reports/{filename}'


# 视图函数
report_dashboard = ProgressReportView.report_dashboard
upload_data = ProgressReportView.upload_data
generate_report = ProgressReportView.generate_report
export_report = ProgressReportView.export_report
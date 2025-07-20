"""
PUBG游戏数据可视化API路由
包含所有数据分析和可视化相关的API端点
"""

import os
import pandas as pd
import numpy as np
import joblib
import asyncio
from flask import Blueprint, jsonify, request
from scipy.ndimage import gaussian_filter
from storage.database import get_history_database
from services.advice import PubgAdviceService, AdviceRequest, create_pubg_advice_service
from config.config import load_config

# 创建蓝图
api_bp = Blueprint('api', __name__)

# 全局数据变量
agg_data = None
death_data = None
prediction_model = None
pubg_advice_service = None

# 模型特征名称（必须与训练时保持一致）
FEATURE_NAMES = [
    'game_size', 'party_size', 'player_assists', 'player_dbno',
    'player_dist_ride', 'player_dist_walk', 'player_dmg',
    'player_kills', 'player_survive_time', 'mode_tpp'
]

def load_game_data():
    """加载游戏数据和预测模型"""
    global agg_data, death_data, prediction_model, pubg_advice_service
    try:
        # 获取数据文件路径（相对于项目根目录）
        data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')


        # 加载聚合统计数据
        agg_data = pd.read_csv(os.path.join(data_dir, 'agg_match_stats_0_half.csv'))
        agg_data.drop_duplicates(inplace=True)
        agg_data['won'] = agg_data['team_placement'] == 1
        agg_data['drove'] = agg_data['player_dist_ride'] != 0

        # 加载击杀数据
        death_data = pd.read_csv(os.path.join(data_dir, 'kill_match_stats_final_0_half.csv'))

        print("游戏数据加载成功")
        print(f"聚合数据形状: {agg_data.shape}")
        print(f"击杀数据形状: {death_data.shape}")

        # 加载预测模型
        model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'model', 'pubg_winner_model.joblib')

        try:
            prediction_model = joblib.load(model_path)
            print("PUBG吃鸡预测模型加载成功")
        except FileNotFoundError:
            print(f"警告：预测模型文件未找到: {model_path}")
            prediction_model = None
        except Exception as e:
            print(f"预测模型加载失败: {e}")
            prediction_model = None

        # 初始化AI建议服务
        try:
            ai_config = load_config()
            pubg_advice_service = create_pubg_advice_service(ai_config)
            print("PUBG AI建议服务初始化成功")
        except Exception as e:
            print(f"AI建议服务初始化失败: {e}")
            pubg_advice_service = None

        return True
    except Exception as e:
        print(f"数据加载失败: {e}")
        return False

def heatmap(x, y, s, bins=100):
    """生成热力图数据"""
    heatmap_data, xedges, yedges = np.histogram2d(x, y, bins=bins)
    heatmap_data = gaussian_filter(heatmap_data, sigma=s)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    return heatmap_data.T, extent

# API端点 - 测试接口
@api_bp.route('/test')
def test():
    """简单测试端点"""
    return jsonify({
        'message': 'PUBG数据API正常工作',
        'data_loaded': agg_data is not None and death_data is not None,
        'model_loaded': prediction_model is not None,
        'agg_data_shape': agg_data.shape if agg_data is not None else None,
        'death_data_shape': death_data.shape if death_data is not None else None
    })

# API端点 - 击杀人数与吃鸡概率关系
@api_bp.route('/kill-win-rate')
def kill_win_rate():
    """击杀人数与吃鸡概率关系数据"""
    if agg_data is None:
        return jsonify({'error': '数据未加载'}), 500
    
    try:
        # 筛选击杀数小于40的数据
        filtered_data = agg_data.loc[agg_data['player_kills'] < 40, ['player_kills', 'won']]
        win_rate_data = filtered_data.groupby('player_kills').won.mean()
        
        result = []
        for kills, rate in win_rate_data.items():
            result.append({
                'kills': int(kills),
                'win_rate': float(rate)
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API端点 - 队伍规模与击杀数分布
@api_bp.route('/party-size-kills')
def party_size_kills():
    """队伍规模与击杀数分布数据"""
    if agg_data is None:
        return jsonify({'error': '数据未加载'}), 500
    
    try:
        # 筛选击杀数小于等于10的数据
        filtered_data = agg_data.loc[agg_data['player_kills'] <= 10, ['party_size', 'player_kills']]
        
        result = {}
        for party_size in sorted(filtered_data['party_size'].unique()):
            party_data = filtered_data[filtered_data['party_size'] == party_size]
            kill_counts = party_data['player_kills'].value_counts().sort_index()
            
            result[f'party_{int(party_size)}'] = [
                {'kills': int(kills), 'count': int(count)} 
                for kills, count in kill_counts.items()
            ]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API端点 - 助攻次数与吃鸡概率关系
@api_bp.route('/assist-win-rate')
def assist_win_rate():
    """助攻次数与吃鸡概率关系数据"""
    if agg_data is None:
        return jsonify({'error': '数据未加载'}), 500
    
    try:
        # 筛选非单人模式数据
        filtered_data = agg_data.loc[agg_data['party_size'] != 1, ['player_assists', 'won']]
        assist_win_rate = filtered_data.groupby('player_assists').won.mean()
        
        result = []
        for assists, rate in assist_win_rate.items():
            result.append({
                'assists': int(assists),
                'win_rate': float(rate)
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API端点 - 搭乘车辆里程与吃鸡概率关系
@api_bp.route('/vehicle-distance-win')
def vehicle_distance_win():
    """搭乘车辆里程与吃鸡概率关系数据"""
    if agg_data is None:
        return jsonify({'error': '数据未加载'}), 500
    
    try:
        # 筛选搭乘距离小于12000的数据
        filtered_data = agg_data.loc[agg_data['player_dist_ride'] < 12000, ['player_dist_ride', 'won']]
        
        # 创建距离区间
        labels = ["0-1k", "1-2k", "2-3k", "3-4k", "4-5k", "5-6k", 
                 "6-7k", "7-8k", "8-9k", "9-10k", "10-11k", "11-12k"]
        
        filtered_data['distance_range'] = pd.cut(filtered_data['player_dist_ride'], 12, labels=labels)
        win_rate_by_distance = filtered_data.groupby('distance_range', observed=False).won.mean()
        
        result = []
        for distance_range, rate in win_rate_by_distance.items():
            result.append({
                'distance_range': str(distance_range),
                'win_rate': float(rate) if not pd.isna(rate) else 0
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API端点 - 武器击杀统计
@api_bp.route('/weapon-kills')
def weapon_kills():
    """武器击杀统计数据"""
    if death_data is None:
        return jsonify({'error': '数据未加载'}), 500

    try:
        # 筛选有效击杀数据
        valid_kills = death_data.loc[
            (death_data['killer_position_x'] > 0) &
            (death_data['victim_position_x'] > 0) &
            (death_data['killed_by'] != 'Down and Out'), :
        ]

        erangel_kills = valid_kills[valid_kills['map'] == 'ERANGEL']
        miramar_kills = valid_kills[valid_kills['map'] == 'MIRAMAR']

        # 获取前10武器击杀统计
        erangel_weapon_stats = erangel_kills['killed_by'].value_counts()[:10]
        miramar_weapon_stats = miramar_kills['killed_by'].value_counts()[:10]

        result = {
            'erangel': [
                {'weapon': weapon, 'kills': int(kills)}
                for weapon, kills in erangel_weapon_stats.items()
            ],
            'miramar': [
                {'weapon': weapon, 'kills': int(kills)}
                for weapon, kills in miramar_weapon_stats.items()
            ]
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API端点 - 击杀距离分布
@api_bp.route('/kill-distance')
def kill_distance():
    """击杀距离分布数据"""
    if death_data is None:
        return jsonify({'error': '数据未加载'}), 500

    try:
        # 筛选有效击杀数据
        valid_kills = death_data.loc[
            (death_data['killer_position_x'] > 0) &
            (death_data['victim_position_x'] > 0) &
            (death_data['killed_by'] != 'Down and Out'), :
        ]

        erangel_kills = valid_kills[valid_kills['map'] == 'ERANGEL'].copy()

        # 计算击杀距离
        erangel_kills['distance'] = np.sqrt(
            ((erangel_kills['killer_position_x'] - erangel_kills['victim_position_x']) / 100) ** 2 +
            ((erangel_kills['killer_position_y'] - erangel_kills['victim_position_y']) / 100) ** 2
        )

        # 筛选距离小于400米的数据
        distance_data = erangel_kills.loc[erangel_kills['distance'] < 400, 'distance']

        # 创建直方图数据
        hist, bin_edges = np.histogram(distance_data, bins=50)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        result = [
            {'distance': float(center), 'count': int(count)}
            for center, count in zip(bin_centers, hist)
        ]

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API端点 - 不同距离武器击杀统计
@api_bp.route('/weapon-distance-analysis')
def weapon_distance_analysis():
    """不同距离武器击杀统计数据"""
    if death_data is None:
        return jsonify({'error': '数据未加载'}), 500

    try:
        # 筛选有效击杀数据
        valid_kills = death_data.loc[
            (death_data['killer_position_x'] > 0) &
            (death_data['victim_position_x'] > 0) &
            (death_data['killed_by'] != 'Down and Out'), :
        ]

        erangel_kills = valid_kills[valid_kills['map'] == 'ERANGEL'].copy()
        miramar_kills = valid_kills[valid_kills['map'] == 'MIRAMAR'].copy()

        # 计算击杀距离
        erangel_kills['distance'] = np.sqrt(
            ((erangel_kills['killer_position_x'] - erangel_kills['victim_position_x']) / 100) ** 2 +
            ((erangel_kills['killer_position_y'] - erangel_kills['victim_position_y']) / 100) ** 2
        )

        miramar_kills['distance'] = np.sqrt(
            ((miramar_kills['killer_position_x'] - miramar_kills['victim_position_x']) / 100) ** 2 +
            ((miramar_kills['killer_position_y'] - miramar_kills['victim_position_y']) / 100) ** 2
        )

        result = {
            'erangel': {
                'sniper': erangel_kills.loc[
                    (erangel_kills['distance'] > 50) & (erangel_kills['distance'] < 1500),
                    'killed_by'
                ].value_counts()[:10].to_dict(),
                'melee': erangel_kills.loc[
                    erangel_kills['distance'] < 50,
                    'killed_by'
                ].value_counts()[:10].to_dict()
            },
            'miramar': {
                'sniper': miramar_kills.loc[
                    (miramar_kills['distance'] > 50) & (miramar_kills['distance'] < 1500),
                    'killed_by'
                ].value_counts()[:10].to_dict(),
                'melee': miramar_kills.loc[
                    miramar_kills['distance'] < 50,
                    'killed_by'
                ].value_counts()[:10].to_dict()
            }
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API端点 - 交互式武器分析数据
@api_bp.route('/interactive-weapon-analysis')
def interactive_weapon_analysis():
    """交互式武器分析数据"""
    if death_data is None:
        return jsonify({'error': '数据未加载'}), 500

    try:
        # 筛选有效击杀数据
        valid_kills = death_data.loc[
            (death_data['killer_position_x'] > 0) &
            (death_data['victim_position_x'] > 0) &
            (death_data['killed_by'] != 'Down and Out'), :
        ]

        erangel_kills = valid_kills[valid_kills['map'] == 'ERANGEL'].copy()
        miramar_kills = valid_kills[valid_kills['map'] == 'MIRAMAR'].copy()

        # 计算击杀距离并筛选
        erangel_kills['distance'] = np.sqrt(
            ((erangel_kills['killer_position_x'] - erangel_kills['victim_position_x']) / 100) ** 2 +
            ((erangel_kills['killer_position_y'] - erangel_kills['victim_position_y']) / 100) ** 2
        )
        erangel_kills = erangel_kills[erangel_kills['distance'] < 800]

        miramar_kills['distance'] = np.sqrt(
            ((miramar_kills['killer_position_x'] - miramar_kills['victim_position_x']) / 100) ** 2 +
            ((miramar_kills['killer_position_y'] - miramar_kills['victim_position_y']) / 100) ** 2
        )
        miramar_kills = miramar_kills[miramar_kills['distance'] < 800]

        # 获取前10武器
        top_weapons_erg = list(erangel_kills['killed_by'].value_counts()[:10].index)
        top_weapons_mrm = list(miramar_kills['killed_by'].value_counts()[:10].index)

        result = {
            'erangel': {
                'weapons': top_weapons_erg,
                'data': erangel_kills[erangel_kills['killed_by'].isin(top_weapons_erg)][
                    ['killed_by', 'distance']
                ].to_dict('records')
            },
            'miramar': {
                'weapons': top_weapons_mrm,
                'data': miramar_kills[miramar_kills['killed_by'].isin(top_weapons_mrm)][
                    ['killed_by', 'distance']
                ].to_dict('records')
            }
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API端点 - PUBG吃鸡概率预测
@api_bp.route('/predict', methods=['POST'])
def predict_win_probability():
    """PUBG吃鸡概率预测"""
    if prediction_model is None:
        return jsonify({'error': '预测模型未加载，无法进行预测'}), 500

    try:
        # 获取POST请求的JSON数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供有效的JSON数据'}), 400

        print(f"收到预测请求数据: {data}")

        # 数据验证和预处理
        required_fields = ['game_size', 'party_size', 'player_kills', 'player_dmg',
                          'player_dbno', 'player_assists', 'player_survive_time',
                          'player_dist_walk', 'player_dist_ride']

        # 检查必需字段
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'缺少必需字段: {missing_fields}'}), 400

        # 数据类型转换和范围验证
        try:
            input_data = {}

            # 游戏总人数 (50-100)
            game_size = float(data['game_size'])
            if not 50 <= game_size <= 100:
                return jsonify({'error': '游戏总人数应在50-100之间'}), 400
            input_data['game_size'] = [game_size]

            # 队伍规模 (1-4)
            party_size = float(data['party_size'])
            if not 1 <= party_size <= 4:
                return jsonify({'error': '队伍规模应在1-4之间'}), 400
            input_data['party_size'] = [party_size]

            # 击杀数 (0-50)
            player_kills = float(data['player_kills'])
            if not 0 <= player_kills <= 50:
                return jsonify({'error': '击杀数应在0-50之间'}), 400
            input_data['player_kills'] = [player_kills]

            # 造成伤害 (0-10000)
            player_dmg = float(data['player_dmg'])
            if not 0 <= player_dmg <= 10000:
                return jsonify({'error': '造成伤害应在0-10000之间'}), 400
            input_data['player_dmg'] = [player_dmg]

            # 击倒数 (0-50)
            player_dbno = float(data['player_dbno'])
            if not 0 <= player_dbno <= 50:
                return jsonify({'error': '击倒数应在0-50之间'}), 400
            input_data['player_dbno'] = [player_dbno]

            # 助攻数 (0-20)
            player_assists = float(data['player_assists'])
            if not 0 <= player_assists <= 20:
                return jsonify({'error': '助攻数应在0-20之间'}), 400
            input_data['player_assists'] = [player_assists]

            # 生存时间 (0-3600秒)
            player_survive_time = float(data['player_survive_time'])
            if not 0 <= player_survive_time <= 3600:
                return jsonify({'error': '生存时间应在0-3600秒之间'}), 400
            input_data['player_survive_time'] = [player_survive_time]

            # 步行距离 (0-20000米)
            player_dist_walk = float(data['player_dist_walk'])
            if not 0 <= player_dist_walk <= 20000:
                return jsonify({'error': '步行距离应在0-20000米之间'}), 400
            input_data['player_dist_walk'] = [player_dist_walk]

            # 载具行驶距离 (0-20000米)
            player_dist_ride = float(data['player_dist_ride'])
            if not 0 <= player_dist_ride <= 20000:
                return jsonify({'error': '载具行驶距离应在0-20000米之间'}), 400
            input_data['player_dist_ride'] = [player_dist_ride]

            # 模式固定为TPP
            input_data['mode_tpp'] = [1]

        except (ValueError, TypeError) as e:
            return jsonify({'error': f'数据类型错误: {str(e)}'}), 400

        # 创建DataFrame并确保列顺序正确
        df = pd.DataFrame(input_data)

        # 确保所有特征都存在，缺失的设为0
        for col in FEATURE_NAMES:
            if col not in df.columns:
                df[col] = 0

        # 按正确顺序排列列
        df = df[FEATURE_NAMES]

        print(f"预测输入数据:\n{df.to_string()}")

        # 进行预测
        prediction_proba = prediction_model.predict_proba(df)[:, 1]
        win_probability = float(prediction_proba[0])

        # 计算置信度
        confidence = "high" if win_probability > 0.7 or win_probability < 0.3 else "medium"
        if 0.4 <= win_probability <= 0.6:
            confidence = "low"

        result = {
            'probability': round(win_probability, 4),
            'confidence': confidence,
            'percentage': round(win_probability * 100, 2)
        }

        print(f"预测结果: {result}")

        # 保存预测结果到数据库（tactics字段暂时为空，等待AI建议生成）
        try:
            db = get_history_database()
            record_id = db.save_prediction(data, result, tactics=None)
            result['record_id'] = record_id
            print(f"预测记录已保存到数据库，ID: {record_id}，等待AI建议生成")
        except Exception as db_error:
            print(f"保存预测记录到数据库失败: {db_error}")
            # 不影响预测结果返回，只记录错误

        return jsonify(result)

    except Exception as e:
        print(f"预测过程中发生错误: {e}")
        return jsonify({'error': f'预测失败: {str(e)}'}), 500

# API端点 - 获取预测历史记录
@api_bp.route('/history')
def get_prediction_history():
    """获取预测历史记录（支持新旧分页参数）"""
    try:
        # 获取查询参数 - 支持新的page/per_page和旧的limit/offset
        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', type=int)
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)

        db = get_history_database()

        # 如果使用新的分页参数
        if page is not None or per_page is not None:
            # 参数验证和默认值
            if page is None or page < 1:
                page = 1
            if per_page is None or per_page < 1:
                per_page = 10
            if per_page > 100:
                per_page = 100

            try:
                history, pagination_info = db.get_history_paginated(page=page, per_page=per_page)

                result = {
                    'history': history,
                    'pagination': pagination_info
                }

                return jsonify(result)

            except Exception as e:
                return jsonify({'error': f'分页参数无效: {str(e)}'}), 400

        # 使用旧的limit/offset参数（向后兼容）
        else:
            if limit is None:
                limit = 50
            if offset is None:
                offset = 0

            # 限制查询数量
            if limit > 100:
                limit = 100
            if limit < 1:
                limit = 10
            if offset < 0:
                offset = 0

            history = db.get_history(limit=limit, offset=offset)
            total_count = db.get_history_count()

            result = {
                'history': history,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_count
            }

            return jsonify(result)

    except Exception as e:
        print(f"获取历史记录失败: {e}")
        return jsonify({'error': f'获取历史记录失败: {str(e)}'}), 500

# API端点 - 获取预测统计信息
@api_bp.route('/history/stats')
def get_prediction_statistics():
    """获取预测统计信息"""
    try:
        db = get_history_database()
        stats = db.get_statistics()
        return jsonify(stats)

    except Exception as e:
        print(f"获取统计信息失败: {e}")
        return jsonify({'error': f'获取统计信息失败: {str(e)}'}), 500

# API端点 - 删除历史记录
@api_bp.route('/history/<int:record_id>', methods=['DELETE'])
def delete_prediction_record(record_id):
    """删除指定的预测历史记录"""
    try:
        db = get_history_database()
        success = db.delete_history(record_id)

        if success:
            return jsonify({'message': f'记录 {record_id} 删除成功'})
        else:
            return jsonify({'error': f'未找到记录 {record_id}'}), 404

    except Exception as e:
        print(f"删除历史记录失败: {e}")
        return jsonify({'error': f'删除历史记录失败: {str(e)}'}), 500


# API端点 - AI生成PUBG游戏建议
@api_bp.route('/generate-advice', methods=['POST'])
def generate_pubg_advice():
    """生成PUBG游戏建议"""
    if pubg_advice_service is None:
        return jsonify({'error': 'AI建议服务未初始化，请检查DeepSeek API配置'}), 500

    try:
        # 获取请求数据
        data = request.get_json() or {}
        prediction_record_id = data.get('record_id')

        print(f"收到AI建议生成请求，关联记录ID: {prediction_record_id}")

        # 创建建议请求
        advice_request = AdviceRequest()

        # 使用asyncio运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            advice_response = loop.run_until_complete(
                pubg_advice_service.generate_advice(advice_request)
            )
        finally:
            loop.close()

        print("AI建议生成成功")

        # 保存或更新AI建议到数据库
        db_saved = False
        record_id = None
        operation = "created"

        try:
            db = get_history_database()

            if prediction_record_id:
                # 更新现有预测记录的tactics字段
                success = db.update_tactics(prediction_record_id, advice_response.content)
                if success:
                    db_saved = True
                    record_id = prediction_record_id
                    operation = "updated"
                    print(f"AI建议已更新到预测记录，ID: {record_id}")
                else:
                    # 如果更新失败，创建新记录
                    record_id = db.save_ai_advice(advice_response.content)
                    db_saved = True
                    operation = "created"
                    print(f"预测记录不存在，已创建新的AI建议记录，ID: {record_id}")
            else:
                # 没有关联的预测记录，创建新记录
                record_id = db.save_ai_advice(advice_response.content)
                db_saved = True
                operation = "created"
                print(f"AI建议已保存为新记录，ID: {record_id}")

        except Exception as db_error:
            print(f"保存AI建议到数据库失败: {db_error}")
            # 不影响主要功能，继续返回建议内容

        return jsonify({
            'success': True,
            'advice': advice_response.content,
            'message': 'AI建议生成成功',
            'database_saved': db_saved,
            'record_id': record_id,
            'operation': operation
        })

    except ValueError as e:
        print(f"AI建议生成失败: {e}")
        return jsonify({'error': f'AI建议生成失败: {str(e)}'}), 500
    except Exception as e:
        print(f"AI建议生成过程中发生错误: {e}")
        return jsonify({'error': f'AI建议生成失败: {str(e)}'}), 500

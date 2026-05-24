// 中国省市区数据 — 省份 + 主要城市
export const regionData = [
  { value: '北京市', label: '北京市', children: [
    { value: '朝阳区', label: '朝阳区' }, { value: '海淀区', label: '海淀区' },
    { value: '东城区', label: '东城区' }, { value: '西城区', label: '西城区' },
    { value: '丰台区', label: '丰台区' }, { value: '石景山区', label: '石景山区' },
    { value: '通州区', label: '通州区' }, { value: '大兴区', label: '大兴区' },
    { value: '昌平区', label: '昌平区' }, { value: '顺义区', label: '顺义区' },
  ]},
  { value: '上海市', label: '上海市', children: [
    { value: '浦东新区', label: '浦东新区' }, { value: '徐汇区', label: '徐汇区' },
    { value: '黄浦区', label: '黄浦区' }, { value: '静安区', label: '静安区' },
    { value: '长宁区', label: '长宁区' }, { value: '普陀区', label: '普陀区' },
    { value: '虹口区', label: '虹口区' }, { value: '杨浦区', label: '杨浦区' },
    { value: '闵行区', label: '闵行区' }, { value: '宝山区', label: '宝山区' },
  ]},
  { value: '天津市', label: '天津市', children: [
    { value: '和平区', label: '和平区' }, { value: '南开区', label: '南开区' },
    { value: '河西区', label: '河西区' }, { value: '河东区', label: '河东区' },
    { value: '河北区', label: '河北区' }, { value: '红桥区', label: '红桥区' },
    { value: '滨海新区', label: '滨海新区' },
  ]},
  { value: '重庆市', label: '重庆市', children: [
    { value: '渝中区', label: '渝中区' }, { value: '江北区', label: '江北区' },
    { value: '南岸区', label: '南岸区' }, { value: '沙坪坝区', label: '沙坪坝区' },
    { value: '九龙坡区', label: '九龙坡区' }, { value: '渝北区', label: '渝北区' },
  ]},
  { value: '广东省', label: '广东省', children: [
    { value: '广州市', label: '广州市' }, { value: '深圳市', label: '深圳市' },
    { value: '东莞市', label: '东莞市' }, { value: '佛山市', label: '佛山市' },
    { value: '珠海市', label: '珠海市' }, { value: '中山市', label: '中山市' },
    { value: '惠州市', label: '惠州市' }, { value: '汕头市', label: '汕头市' },
  ]},
  { value: '浙江省', label: '浙江省', children: [
    { value: '杭州市', label: '杭州市' }, { value: '宁波市', label: '宁波市' },
    { value: '温州市', label: '温州市' }, { value: '嘉兴市', label: '嘉兴市' },
    { value: '湖州市', label: '湖州市' }, { value: '绍兴市', label: '绍兴市' },
    { value: '金华市', label: '金华市' }, { value: '台州市', label: '台州市' },
  ]},
  { value: '江苏省', label: '江苏省', children: [
    { value: '南京市', label: '南京市' }, { value: '苏州市', label: '苏州市' },
    { value: '无锡市', label: '无锡市' }, { value: '常州市', label: '常州市' },
    { value: '南通市', label: '南通市' }, { value: '徐州市', label: '徐州市' },
    { value: '扬州市', label: '扬州市' }, { value: '镇江市', label: '镇江市' },
  ]},
  { value: '四川省', label: '四川省', children: [
    { value: '成都市', label: '成都市' }, { value: '绵阳市', label: '绵阳市' },
    { value: '德阳市', label: '德阳市' }, { value: '宜宾市', label: '宜宾市' },
    { value: '南充市', label: '南充市' }, { value: '泸州市', label: '泸州市' },
  ]},
  { value: '湖北省', label: '湖北省', children: [
    { value: '武汉市', label: '武汉市' }, { value: '宜昌市', label: '宜昌市' },
    { value: '襄阳市', label: '襄阳市' }, { value: '荆州市', label: '荆州市' },
    { value: '黄石市', label: '黄石市' }, { value: '十堰市', label: '十堰市' },
  ]},
  { value: '湖南省', label: '湖南省', children: [
    { value: '长沙市', label: '长沙市' }, { value: '株洲市', label: '株洲市' },
    { value: '湘潭市', label: '湘潭市' }, { value: '衡阳市', label: '衡阳市' },
    { value: '岳阳市', label: '岳阳市' }, { value: '常德市', label: '常德市' },
  ]},
  { value: '山东省', label: '山东省', children: [
    { value: '济南市', label: '济南市' }, { value: '青岛市', label: '青岛市' },
    { value: '烟台市', label: '烟台市' }, { value: '潍坊市', label: '潍坊市' },
    { value: '临沂市', label: '临沂市' }, { value: '淄博市', label: '淄博市' },
  ]},
  { value: '福建省', label: '福建省', children: [
    { value: '福州市', label: '福州市' }, { value: '厦门市', label: '厦门市' },
    { value: '泉州市', label: '泉州市' }, { value: '漳州市', label: '漳州市' },
    { value: '莆田市', label: '莆田市' }, { value: '龙岩市', label: '龙岩市' },
  ]},
  { value: '安徽省', label: '安徽省', children: [
    { value: '合肥市', label: '合肥市' }, { value: '芜湖市', label: '芜湖市' },
    { value: '蚌埠市', label: '蚌埠市' }, { value: '马鞍山市', label: '马鞍山市' },
  ]},
  { value: '河南省', label: '河南省', children: [
    { value: '郑州市', label: '郑州市' }, { value: '洛阳市', label: '洛阳市' },
    { value: '开封市', label: '开封市' }, { value: '南阳市', label: '南阳市' },
    { value: '新乡市', label: '新乡市' }, { value: '许昌市', label: '许昌市' },
  ]},
  { value: '河北省', label: '河北省', children: [
    { value: '石家庄市', label: '石家庄市' }, { value: '唐山市', label: '唐山市' },
    { value: '保定市', label: '保定市' }, { value: '邯郸市', label: '邯郸市' },
    { value: '廊坊市', label: '廊坊市' }, { value: '沧州市', label: '沧州市' },
  ]},
  { value: '辽宁省', label: '辽宁省', children: [
    { value: '沈阳市', label: '沈阳市' }, { value: '大连市', label: '大连市' },
    { value: '鞍山市', label: '鞍山市' }, { value: '锦州市', label: '锦州市' },
  ]},
  { value: '陕西省', label: '陕西省', children: [
    { value: '西安市', label: '西安市' }, { value: '咸阳市', label: '咸阳市' },
    { value: '宝鸡市', label: '宝鸡市' }, { value: '渭南市', label: '渭南市' },
  ]},
  { value: '其他省份', label: '其他省份', children: [
    { value: '黑龙江省', label: '黑龙江省' }, { value: '吉林省', label: '吉林省' },
    { value: '山西省', label: '山西省' }, { value: '江西省', label: '江西省' },
    { value: '贵州省', label: '贵州省' }, { value: '云南省', label: '云南省' },
    { value: '海南省', label: '海南省' }, { value: '甘肃省', label: '甘肃省' },
    { value: '青海省', label: '青海省' }, { value: '内蒙古', label: '内蒙古' },
    { value: '广西', label: '广西' }, { value: '西藏', label: '西藏' },
    { value: '宁夏', label: '宁夏' }, { value: '新疆', label: '新疆' },
    { value: '香港', label: '香港' }, { value: '澳门', label: '澳门' },
    { value: '台湾', label: '台湾' },
  ]},
]

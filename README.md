# code
ALAN代码
①Script-4 wh.sql：生成horiz、verti_pts
②8 重分配3.sql——》 3_preprocess.py ：LULC-based超分辨率，结合40m和10m，获得fishnet_10内每个用地类型每个波段的辐射值
③（最耗时）5 生成horiz_radiance_pts.sql——》5.py用于添加新字段param_s——》5_2.py 用于结合new——pts和tempcombine得到redis——idx ——》运行4_final.py用于新增加字段pts_rad_i,2,3值idx ——》 回到5 生成horiz_radiance_pts.sql：生成新表bdg_horiz_pts_radiance
④Script-6 verti.sql（比较慢）——》7.py：本节空间链接生成建筑h=0的点辐射值，再用py脚本生成表bdg_verti_pts_radiance。

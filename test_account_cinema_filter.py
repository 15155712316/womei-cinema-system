        # 测试影院切换
        if cinemas:
            # 找到有账号的影院进行测试
            test_cinema = None
            for cinema in cinemas:
                cinema_id = cinema.get('cinemaid', '')
                cinema_accounts = [acc for acc in accounts if acc.get('cinemaid') == cinema_id]
                if cinema_accounts:
                    test_cinema = cinema
                    break
            
            if test_cinema:
                cinema_name = test_cinema.get('cinemaShortName', '')
                cinema_id = test_cinema.get('cinemaid', '')
                account_widget._on_cinema_selected(test_cinema)
                
                print(f"✅ 影院切换测试成功 (切换到有账号的影院)")
                print(f"  - 测试影院: {cinema_name} ({cinema_id})")
                print(f"  - 切换后显示账号数量: {len(account_widget.accounts_data)}")
            else:
                print(f"⚠️  所有影院都没有关联账号，使用第一个影院测试")
                account_widget._on_cinema_selected(cinemas[0])
                print(f"  - 切换后显示账号数量: {len(account_widget.accounts_data)}")
        
        # 清理
        account_widget.cleanup() 
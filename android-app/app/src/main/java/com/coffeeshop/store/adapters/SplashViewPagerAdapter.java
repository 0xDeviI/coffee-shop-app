package com.coffeeshop.store.adapters;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentManager;
import androidx.lifecycle.Lifecycle;
import androidx.viewpager2.adapter.FragmentStateAdapter;

import com.coffeeshop.store.fragments.splash.FirstSlide;
import com.coffeeshop.store.fragments.splash.SecondSlide;

public class SplashViewPagerAdapter extends FragmentStateAdapter {
    public SplashViewPagerAdapter(@NonNull FragmentManager fragmentManager, @NonNull Lifecycle lifecycle) {
        super(fragmentManager, lifecycle);
    }

    @NonNull
    @Override
    public Fragment createFragment(int position) {
        switch (position) {
            case 0:
                return new FirstSlide();
            case 1:
                return new SecondSlide();
        }
        return null;
    }

    @Override
    public int getItemCount() {
        return 2;
    }
}

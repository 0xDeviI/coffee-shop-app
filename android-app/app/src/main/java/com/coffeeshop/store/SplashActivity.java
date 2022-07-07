package com.coffeeshop.store;

import androidx.appcompat.app.AppCompatActivity;
import androidx.viewpager2.widget.ViewPager2;

import android.os.Bundle;

import com.coffeeshop.store.adapters.SplashViewPagerAdapter;

public class SplashActivity extends AppCompatActivity {

    ViewPager2 viewPager2;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        detectUIElements();
        defineUIBehaviours();
    }

    private void detectUIElements() {
        viewPager2 = findViewById(R.id.viewPager2);
    }

    private void defineUIBehaviours() {
        viewPager2.setAdapter(new SplashViewPagerAdapter(getSupportFragmentManager(), getLifecycle()));
    }
}
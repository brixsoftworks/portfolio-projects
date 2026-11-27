package com.strictday.di

import com.strictday.enforcement.AndroidEnforcementManager
import com.strictday.enforcement.EnforcementManager
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class EnforcementModule {
    @Binds
    @Singleton
    abstract fun bindEnforcementManager(impl: AndroidEnforcementManager): EnforcementManager
}
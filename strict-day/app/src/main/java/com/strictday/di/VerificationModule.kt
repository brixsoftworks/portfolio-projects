package com.strictday.di

import com.strictday.verification.AndroidVerificationEngine
import com.strictday.verification.DefaultRuleEvaluator
import com.strictday.verification.VerificationEngine
import com.strictday.verification.VerificationRuleEvaluator
import dagger.Binds
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object VerificationModule {

    @Provides
    @Singleton
    fun provideVerificationEvaluator(): VerificationRuleEvaluator = DefaultRuleEvaluator()
}

@Module
@InstallIn(SingletonComponent::class)
abstract class VerificationEngineModule {

    @Binds
    @Singleton
    abstract fun bindVerificationEngine(impl: AndroidVerificationEngine): VerificationEngine
}

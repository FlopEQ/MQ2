/*
 * MacroQuest: The extension platform for EverQuest
 * Copyright (C) 2002-present MacroQuest Authors
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License, version 2, as published by
 * the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 */

#include "pch.h"
#include "GraphicsResources.h"

#include "MQ2Main.h"

#include "eqlib/graphics/GraphicsEngine.h"
#include "eqlib/graphics/ResourceManagerInterface.h"
#include "mq/api/Textures.h"

namespace mq {

//============================================================================

static std::vector<MQTexture*> s_textures;
static bool s_shutdown = false;
static bool s_graphicsResourcesReleased = false;

static int s_renderCallbacksId = -1;

//============================================================================

MQTexture* CreateTexture(std::string_view filename)
{
	MQTexture* newTexture = nullptr;

	if (!s_shutdown && EQGraphicsBaseAddress != 0
		&& pGraphicsEngine && pGraphicsEngine->pResourceManager)
	{
		newTexture = new MQTexture(filename);
		if (!newTexture->IsValid())
		{
			delete newTexture;
			newTexture = nullptr;
		}
	}

	return newTexture;
}

MQTexture* GetTexture(std::string_view filename)
{
	auto findIter = std::find_if(begin(s_textures), end(s_textures),
		[&filename](MQTexture* texture) { return texture->GetFilename() == filename; });

	return findIter == end(s_textures) ? nullptr : *findIter;
}

void DestroyTexture(MQTexture* texture)
{
	delete texture;
}

MQTexturePtr CreateTexturePtr(std::string_view filename)
{
	return std::shared_ptr<MQTexture>(CreateTexture(filename), [](MQTexture* tex) { DestroyTexture(tex); });
}

//============================================================================

MQTexture::MQTexture(std::string_view name)
	: m_name(name)
{
	AcquireTexture();

	if (m_bmi)
	{
		m_bmi->Name = m_name.c_str();
		m_bmi->pBmp->m_nTrackingType = 2; // EQG

		s_textures.push_back(this);
	}
}

MQTexture::~MQTexture()
{
	if (m_bmi && EQGraphicsBaseAddress != 0
		&& pGraphicsEngine && pGraphicsEngine->pResourceManager)
	{
		ReleaseTexture();
	}

	if (!s_shutdown)
	{
		s_textures.erase(std::remove(begin(s_textures), end(s_textures), this), end(s_textures));
	}
}

void MQTexture::AcquireTexture()
{
	if (m_bmi == nullptr && EQGraphicsBaseAddress != 0
		&& pGraphicsEngine && pGraphicsEngine->pResourceManager)
	{
		BMI* bmi = pGraphicsEngine->pResourceManager->CreateBMI(m_name.c_str(), m_name.c_str(),
			nullptr, eMemoryPoolManagerTypePersistent);

		if (!bmi->pBmp)
		{
			pGraphicsEngine->pResourceManager->DestroyBMI(bmi);
		}
		else
		{
			if (bmi->pBmp->GetD3DTexture() == nullptr)
			{
				pGraphicsEngine->pResourceManager->DestroyBMI(bmi);
			}
			else
			{
				m_bmi = bmi;
			}
		}
	}
}

void MQTexture::ReleaseTexture()
{
	if (m_bmi != nullptr)
	{
		pGraphicsEngine->pResourceManager->DestroyBMI(m_bmi);
		m_bmi = nullptr;
	}
}

ImTextureID MQTexture::GetTextureID() const
{
	if (m_bmi && m_bmi->pBmp)
	{
#if HAS_DIRECTX_11
		return m_bmi->pBmp;
#else
		return m_bmi->pBmp->GetTexture();
#endif
	}
	
	return nullptr;
}

CXSize MQTexture::GetTextureSize() const
{
	if (m_bmi && m_bmi->pBmp)
	{
		return CXSize(m_bmi->pBmp->m_uWidth, m_bmi->pBmp->m_uHeight);
	}

	return CXSize();
}

//============================================================================

static void GraphicsResources_CreateDeviceObjects()
{
	if (EQGraphicsBaseAddress != 0 && pGraphicsEngine && pGraphicsEngine->pResourceManager)
	{
		for (MQTexture* texture : s_textures)
		{
			texture->AcquireTexture();
		}
	}
}

static void GraphicsResources_InvalidateDeviceObjects()
{
	if (EQGraphicsBaseAddress != 0 && pGraphicsEngine && pGraphicsEngine->pResourceManager)
	{
		for (MQTexture* texture : s_textures)
		{
			texture->ReleaseTexture();
		}
	}
}

static void GraphicsResources_RegisterCallbacks()
{
	if (s_renderCallbacksId != -1)
		return;

	MQRenderCallbacks callbacks;
	callbacks.CreateDeviceObjects = GraphicsResources_CreateDeviceObjects;
	callbacks.InvalidateDeviceObjects = GraphicsResources_InvalidateDeviceObjects;

	s_renderCallbacksId = AddRenderCallbacks(callbacks);
}

void GraphicsResources_Initialize()
{
	s_shutdown = false;
	s_graphicsResourcesReleased = false;
	GraphicsResources_RegisterCallbacks();
}

void GraphicsResources_ReleaseForGraphicsShutdown()
{
	if (s_graphicsResourcesReleased)
		return;

	if (s_renderCallbacksId != -1)
	{
		RemoveRenderCallbacks(s_renderCallbacksId);
		s_renderCallbacksId = -1;
	}
	else
	{
		GraphicsResources_InvalidateDeviceObjects();
	}

	s_graphicsResourcesReleased = true;
}

void GraphicsResources_RestoreAfterGraphicsStartup()
{
	if (!s_shutdown)
	{
		GraphicsResources_RegisterCallbacks();
		s_graphicsResourcesReleased = false;
	}
}

void GraphicsResources_Shutdown()
{
	if (s_shutdown)
		return;

	s_shutdown = true;
	GraphicsResources_ReleaseForGraphicsShutdown();
	s_textures.clear();
}

//============================================================================

} // namespace mq
